import json
import datetime
import os

import pytz

from odoo import http, _, exceptions
from odoo.http import request, Response


class ProductImageUpload(http.Controller):

    @http.route('/get/folder/last/updated/time/stamp', type='http', csrf=False, auth="public",
                methods=['GET', 'POST', 'OPTIONS'],
                cors="*")
    def get_last_updated_time_stamp(self, **kwargs):
        path = kwargs.get('folder_path')
        try:
            if path:
                existing_root_log = request.env['folder.update.log'].sudo().search([
                    ('root_path', '=', path)], order='root_modified_date desc', limit=1)
                if existing_root_log:
                    desired_timezone = pytz.timezone('Asia/Kolkata')
                    folder_modified_date = existing_root_log.root_modified_date
                    folder_modified_date = folder_modified_date.astimezone(desired_timezone)
                    formatted_date = folder_modified_date.strftime('%Y-%m-%d %H:%M:%S')
                    return Response(json.dumps({'success': True, 'timestamp': formatted_date}),
                                    content_type='application/json',
                                    status=200)
                else:
                    return Response(json.dumps({'success': False, 'msg': 'New Folder'}),
                                    content_type='application/json',
                                    status=400)
        except Exception as e:
            return Response(json.dumps({'success': False, 'msg': str(e)}),
                            content_type='application/json',
                            status=500)

    @http.route('/upload/log/status', type='http', csrf=False, auth="public",
                methods=['GET', 'POST', 'OPTIONS'],
                cors="*")
    def update_log_status(self, **kwargs):
        root = kwargs.get('root_path')
        log_details = request.env['product.image.upload.log'].sudo().search([('root_path', '=', root)], order='id desc',
                                                                            limit=1)
        log_status = [rec for rec in log_details if
                      'Failed' in rec.product_image_upload_line_ids.mapped('log_status')]
        try:
            if log_status:
                log_details.sudo().write({'status': 'Partially Imported', 'import_timestamp': datetime.datetime.now()})
            else:
                log_details.sudo().write({'status': 'Done', 'import_timestamp': datetime.datetime.now()})
            return Response(json.dumps({'success': True}),
                            content_type='application/json',
                            status=200)
        except Exception as e:
            return Response(json.dumps({'success': False, 'msg': str(e)}),
                            content_type='application/json',
                            status=500)

    def create_log_files(self, root_path, dir_name, flag):
        log = request.env['product.image.upload.log']
        log_line = request.env['product.image.upload.log.line']
        product_obj = request.env['product.template'].sudo().search([('barcode', '=', dir_name)])
        logs = log.sudo().search([('root_path', '=', root_path)], order='id desc', limit=1)
        try:
            if int(flag) == 0:
                logs = log.sudo().create({
                    'import_timestamp': datetime.datetime.now(),
                    'salesperson_id': request.env.user.id,
                    'root_path': root_path,
                })

                if not product_obj:
                    # if not found_records:
                    log_line = log_line.sudo().create({
                        'barcode': dir_name,
                        'log_status': 'Failed',
                        'log_message': 'Product with barcode ' + dir_name + ' Doesn\'t Found',
                        'log_type': 'Danger',
                    })
                    logs.sudo().write({'product_image_upload_line_ids': [(4, log_line.id)]})
                    return False
                return logs
            else:
                # if not product_obj:
                #     log_line = log_line.sudo().create({
                #         'barcode': dir_name,
                #         'log_status': 'Failed',
                #         'log_message': 'Product with barcode ' + dir_name + ' Doesn\'t Found',
                #         'log_type': 'Danger',
                #     })
                #     logs.sudo().write({'product_image_upload_line_ids': [(4, log_line.id)]})
                return logs
        except Exception as e:
            return Response(json.dumps({'success': False, 'msg': str(e)}),
                            content_type='application/json',
                            status=500)
    def get_the_file_latest_timestamp(self, dir_path):
        if os.path.exists(dir_path) and os.path.isdir(dir_path):
            files = os.listdir(dir_path)

            if files:
                file_times = [(file, os.path.getatime(os.path.join(dir_path, file))) for file in files]
                file_times.sort(key=lambda x: x[1], reverse=True)
                latest_file, latest_time = file_times[0]
                latest_time = datetime.datetime.utcfromtimestamp(latest_time)
                utc_timezone = pytz.timezone('UTC')
                indian_timezone = pytz.timezone('Asia/Kolkata')

                indian_time = latest_time.replace(tzinfo=utc_timezone).astimezone(
                    indian_timezone)
                print('latest timestamp', indian_time)
                return latest_time
            else:
                print("The folder is empty.")
        else:
            print("The folder doesn't exist or is not a directory.")

    @http.route('/create/empty/dir/log', type='http', csrf=False, auth="public",
                methods=['GET', 'POST', 'OPTIONS'],
                cors="*")
    def create_empty_directory_logs(self, **kwargs):
        root_path = kwargs.get('root')
        prod_barcode = kwargs.get('barcode')
        dir_path = kwargs.get('dir')
        flag_val = kwargs.get('flag')
        dir_modified_time = kwargs.get('dir_modified_time')
        dir_formatted_datetime = datetime.datetime.strptime(dir_modified_time, '%Y-%m-%d %H:%M:%S.%f')
        existing_folder_log = request.env['folder.update.log'].sudo().search([('folder_path', '=', dir_path)],
                                                                             order='id desc', limit=1)
        prod_id = request.env['product.template'].sudo().search([('barcode', '=', prod_barcode)])
        file_latest_time_stamp = self.get_the_file_latest_timestamp(dir_path)

        if file_latest_time_stamp is not None:
            if dir_formatted_datetime > file_latest_time_stamp:
                file_latest_time_stamp = dir_formatted_datetime
        else:
            file_latest_time_stamp = dir_formatted_datetime
        try:
            if not existing_folder_log:
                request.env['folder.update.log'].sudo().create(
                    {'root_path': root_path, 'folder_path': dir_path, 'modified_date': file_latest_time_stamp,
                     'root_modified_date': datetime.datetime.now()})
            else:
                existing_folder_log.sudo().write(
                    {'modified_date': file_latest_time_stamp, 'root_modified_date': datetime.datetime.now(),
                     })

            res = self.create_log_files(root_path, prod_barcode, flag_val)
            if res:
                if prod_id:
                    product_upload_line_ids = [rec for rec in res.product_image_upload_line_ids if
                                               rec.barcode == prod_barcode]
                    if not product_upload_line_ids:
                        log_line = request.env['product.image.upload.log.line'].sudo().create({
                            'barcode': prod_barcode,
                            'log_status': 'Failed',
                            'log_type': 'Danger',
                            'log_message': 'No Files Found In the Folder',
                        })
                        res.sudo().write({'product_image_upload_line_ids': [(4, log_line.id)]})
                    else:
                        [line_id.sudo().write(
                            {'log_status': 'Failed', 'log_type': 'Danger', 'log_message': 'Folder is empty'}) for
                            line_id in product_upload_line_ids]
                else:
                    product_upload_line_ids = [rec for rec in res.product_image_upload_line_ids if
                                               rec.barcode == prod_barcode]
                    if not product_upload_line_ids:
                        log_line = request.env['product.image.upload.log.line'].sudo().create({
                            'barcode': prod_barcode,
                            'log_status': 'Failed',
                            'log_type': 'Danger',
                            'log_message': 'Product with barcode ' + prod_barcode + ' Doesn\'t Found',
                        })
                        res.sudo().write({'product_image_upload_line_ids': [(4, log_line.id)]})
                    else:
                        [line_id.sudo().write(
                            {'log_status': 'Failed', 'log_type': 'Danger',
                             'log_message': 'Product with barcode ' + prod_barcode + ' Doesn\'t Found'}) for
                            line_id in product_upload_line_ids]
                return Response(json.dumps({'success': True, 'msg': 'Product Found', }),
                                content_type='application/json',
                                status=200)
            else:
                return Response(json.dumps({'success': False, 'msg': 'Product Doesn\'t Found'}),
                                content_type='application/json',
                                status=200)
        except Exception as e:
            return Response(json.dumps({'success': False, 'msg': str(e)}),
                            content_type='application/json',
                            status=500)

    @http.route('/get/folder/size', type='http', csrf=False, auth="public",
                methods=['GET', 'POST', 'OPTIONS'], cors="*")
    def get_folder_content_size(self, **kwargs):
        file_size = kwargs.get('file_count')
        path = kwargs.get('dir')
        name = kwargs.get('dir_name')
        dir_mod_time = kwargs.get('dir_modified_time')
        dir_conv_time = datetime.datetime.strptime(dir_mod_time, '%Y-%m-%d %H:%M:%S.%f')
        # dir_accesed_conv_time = datetime.datetime.strptime(dir_accessed_time, '%Y-%m-%d %H:%M:%S.%f')

        try:
            existing_folder_log = request.env['folder.update.log'].sudo().search([('folder_path', '=', path)],
                                                                                 order='root_modified_date desc',
                                                                                 limit=1)
            if existing_folder_log:
                existing_folder_log_size = existing_folder_log.modified_date
                existing_folder_mod_date_str = datetime.datetime.strftime(existing_folder_log_size,
                                                                          '%Y-%m-%d %H:%M:%S.%f')

                if dir_conv_time > existing_folder_log_size or self.check_timestamp_for_images(path,
                                                                                               existing_folder_log_size):
                    response_data = {'dir': name, 'timestamp': dir_mod_time,
                                     'existing_time_stamp': existing_folder_mod_date_str}
                    return Response(json.dumps({'success': True, 'msg': 'Folder updated', 'vals': response_data}),
                                    content_type='application/json',
                                    status=200)
                else:
                    return Response(json.dumps({'success': True, 'msg': 'Folder not updated'}),
                                    content_type='application/json',
                                    status=400)
            else:
                response_data = {'dir': name, 'timestamp': dir_mod_time}
                return Response(json.dumps({'success': True, 'msg': 'Folder not existing', 'vals': response_data}),
                                content_type='application/json',
                                status=200)
        except Exception as e:
            return Response(json.dumps({'success': False, 'msg': str(e)}),
                            content_type='application/json',
                            status=500)

    def check_timestamp_for_images(self, path, existing_folder_timestamp):
        changes_found = False
        for _, _, files in os.walk(path):
            if files:
                for file_name in files:
                    file_path = os.path.join(path, file_name)
                    file_modified_time = self.get_file_accessed_time(file_path)
                    if file_modified_time > existing_folder_timestamp:
                        changes_found = True
                        return changes_found
        return changes_found

    def get_file_accessed_time(self, path):
        time = os.path.getmtime(path)
        file_path_modified_utc = datetime.datetime.utcfromtimestamp(time)
        utc_timezone = pytz.timezone('UTC')
        indian_timezone = pytz.timezone('Asia/Kolkata')

        indian_time = file_path_modified_utc.replace(tzinfo=utc_timezone).astimezone(indian_timezone)
        print('folder accessed', path, indian_time)
        return file_path_modified_utc

    def upload_products_in_odoo(self, *args):
        print("hello")
        base64 = args[0]
        barcode = args[1]
        file_name = args[2]
        file_modified_time = args[3]

        existing_product = request.env['product.template'].sudo().search(
            [('barcode', '=', barcode)])
        extra_media = request.env['product.image'].sudo().search(
            [('name', '=', file_name), ('product_tmpl_id', '=', existing_product.id)])
        if not base64:
            return Response(json.dumps({'success': False, 'msg': 'Product Image is not in base64'}),
                            content_type='application/json',
                            status=400)
        try:
            if existing_product:
                if 'main' in file_name:
                    existing_product.sudo().write({'image_1920': base64})
                elif not extra_media:
                    request.env['product.image'].sudo().create(
                        {'name': file_name if file_name else 'image', 'image_1920': base64,
                         'image_1024': base64,
                         'image_128': base64, 'image_256': base64, 'image_512': base64,
                         'product_tmpl_id': existing_product.id})
                elif extra_media and file_modified_time != 'New Image':
                    extra_media.sudo().write({'name': file_name if file_name else 'image', 'image_1920': base64,
                                              'image_1024': base64,
                                              'image_128': base64, 'image_256': base64, 'image_512': base64,
                                              })
                return Response(json.dumps({'success': True}),
                                content_type='application/json',
                                status=200)
            else:
                return Response(json.dumps({'success': False}),
                                content_type='application/json',
                                status=400)
        except Exception as e:
            return Response(json.dumps({'success': False, 'msg': str(e)}),
                            content_type='application/json',
                            status=500)

        # return Response(json.dumps({'success': True}),
        #                 content_type='application/json',
        #                 status=200)



    @http.route('/upload/root/product/images', type='http', csrf=False, auth="public",
                methods=['GET', 'POST', 'OPTIONS'], cors="*")
    def upload_product_images(self, **kwargs):
        global count
        root_path = kwargs.get('root')
        dir_path = kwargs.get('dir')
        dir_current_time = kwargs.get('dir_modified_time')
        file_current_time = kwargs.get('file_modified_time')
        base6_string = kwargs.get('base64_data')
        product_ref = kwargs.get('barcode')
        img_name = kwargs.get('image_name')
        flag_val = kwargs.get('flag')
        barcode_existing = []
        # if int(flag_val) == 0:
        #     count = 0
        dir_formatted_datetime = datetime.datetime.strptime(dir_current_time, '%Y-%m-%d %H:%M:%S.%f')
        file_latest_time_stamp = self.get_the_file_latest_timestamp(dir_path)

        if file_latest_time_stamp is not None:
            if dir_formatted_datetime > file_latest_time_stamp:
                file_latest_time_stamp = dir_formatted_datetime
        else:
            file_latest_time_stamp = dir_formatted_datetime

        log_data = self.create_log_files(root_path, product_ref, flag_val)
        try:
            if log_data:
                existing_folder_log = request.env['folder.update.log'].sudo().search([('folder_path', '=', dir_path)],
                                                                                     order="root_modified_date desc",
                                                                                     limit=1)
                if existing_folder_log:
                    res = self.upload_products_in_odoo(base6_string, product_ref, img_name, file_current_time)
                    existing_folder_log.sudo().write(
                        {'modified_date': file_latest_time_stamp, 'root_modified_date': datetime.datetime.now(),
                         })
                    if res.status_code == 200:
                        product_upload_line_ids = [rec for rec in log_data.product_image_upload_line_ids if
                                                   rec.barcode == product_ref]
                        if not product_upload_line_ids:
                            log_line = request.env['product.image.upload.log.line'].sudo().create({
                                'barcode': product_ref,
                                'log_status': 'Done',
                                'log_type': 'Success',
                            })
                            log_data.sudo().write({'product_image_upload_line_ids': [(4, log_line.id)]})
                        else:
                            [line_id.sudo().write({'log_status': 'Done'}) for line_id in product_upload_line_ids]

                    elif res.status_code == 500:
                        product_upload_line_ids = [rec for rec in log_data.product_image_upload_line_ids if
                                                   rec.barcode == product_ref]
                        if not product_upload_line_ids:
                            log_line = request.env['product.image.upload.log.line'].sudo().create({
                                'barcode': product_ref,
                                'log_status': 'Failed',
                                'log_type': 'Danger',
                                'log_message': 'Some file couldn\'t be decoded as image file',
                            })
                            log_data.sudo().write({'product_image_upload_line_ids': [(4, log_line.id)]})
                        else:
                            [line_id.sudo().write({'log_status': 'Failed', 'log_type': 'Danger',
                                                   'log_message': 'Some file couldn\'t be decoded as image file'}) for line_id
                             in product_upload_line_ids]
                    else:
                        product_upload_line_ids = [rec for rec in log_data.product_image_upload_line_ids if
                                                   rec.barcode == product_ref]
                        if not product_upload_line_ids:
                            log_line = request.env['product.image.upload.log.line'].sudo().create({
                                'barcode': product_ref,
                                'log_status': 'Failed',
                                'log_type': 'Danger',
                                'log_message': 'Product with barcode ' + product_ref + ' Doesn\'t Found'
                            })
                            log_data.sudo().write({'product_image_upload_line_ids': [(4, log_line.id)]})
                        else:
                            [line_id.sudo().write({'log_status': 'Failed', 'log_type': 'Danger',
                                                   'log_message': 'Product with barcode ' + product_ref + ' Doesn\'t Found'}) for line_id
                             in product_upload_line_ids]
                            # product_upload_line_ids[0].sudo().write(
                            #     {'log_status': 'Failed', 'log_message': 'Product Doesn\'t Uploaded successfully'})
                        # log_line = request.env['product.image.upload.log.line'].sudo().search(
                        #     [('barcode', '=', product_ref)],
                        #     limit=1)

                        # log_data.sudo().write({'product_image_upload_line_ids': [(4, log_line.id)]})
                    return Response(json.dumps({'success': True, 'msg': 'Image Uploaded Successufully'}),
                                    content_type='application/json',
                                    status=200)
                else:
                    request.env['folder.update.log'].sudo().create(
                        {'root_path': root_path, 'folder_path': dir_path, 'modified_date': file_latest_time_stamp,
                         'root_modified_date': datetime.datetime.now()})
                    res = self.upload_products_in_odoo(base6_string, product_ref, img_name, file_current_time)
                    if res.status_code == 200:
                        log_line = request.env['product.image.upload.log.line'].sudo().search(
                            [('barcode', '=', product_ref)],
                            limit=1)
                        if not log_line:
                            log_line = request.env['product.image.upload.log.line'].sudo().create({
                                'barcode': product_ref,
                                'log_status': 'Done',
                                'log_type': 'Success',
                            })
                            log_data.sudo().write({'product_image_upload_line_ids': [(4, log_line.id)]})
                        else:
                            log_line.sudo().write({'log_status': 'Done'})
                            log_data.sudo().write({'product_image_upload_line_ids': [(4, log_line.id)]})
                    elif res.status_code == 500:
                        product_upload_line_ids = [rec for rec in log_data.product_image_upload_line_ids if
                                                   rec.barcode == product_ref]
                        if not product_upload_line_ids:
                            log_line = request.env['product.image.upload.log.line'].sudo().create({
                                'barcode': product_ref,
                                'log_status': 'Failed',
                                'log_type': 'Danger',
                                'log_message': 'Some file couldn\'t be decoded as image file',
                            })
                            log_data.sudo().write({'product_image_upload_line_ids': [(4, log_line.id)]})
                        else:
                            [line_id.sudo().write({'log_status': 'Failed', 'log_type': 'Danger',
                                                   'log_message': 'Some file couldn\'t be decoded as image file'}) for line_id
                             in product_upload_line_ids]
                    # elif res.status_code == 400:
                    #     log_line = request.env['product.image.upload.log.line'].sudo().search(
                    #         [('barcode', '=', product_ref)],
                    #         limit=1)
                    #     if not log_line:
                    #         log_line = request.env['product.image.upload.log.line'].sudo().create({
                    #             'barcode': product_ref,
                    #             'log_status': 'Failed',
                    #             'log_type': 'Danger',
                    #             'log_message': 'Product with barcode ' + product_ref + ' Doesn\'t Found',
                    #         })
                    #         log_data.sudo().write({'product_image_upload_line_ids': [(4, log_line.id)]})
                    #     else:
                    #         log_line.sudo().write({'log_status': 'Failed', 'log_type': 'Danger', 'log_message': 'Product with barcode ' + product_ref + ' Doesn\'t Found'})
                    #         log_data.sudo().write({'product_image_upload_line_ids': [(4, log_line.id)]})
                    else:
                        log_line = request.env['product.image.upload.log.line'].sudo().search(
                            [('barcode', '=', product_ref)],
                            limit=1)
                        if not log_line:
                            log_line = request.env['product.image.upload.log.line'].sudo().create({
                                'barcode': product_ref,
                                'log_status': 'Failed',
                                'log_type': 'Danger',
                                'log_message': 'Product with barcode ' + product_ref + ' Doesn\'t Found'
                            })
                            log_data.sudo().write({'product_image_upload_line_ids': [(4, log_line.id)]})
                            return Response(json.dumps({'success': False, 'msg': 'Product Doesnot Found'}),
                                            content_type='application/json',
                                            status=400)

                        else:
                            log_line.sudo().write(
                                {'log_status': 'Failed', 'log_type': 'Danger', 'log_message': 'Product with barcode ' + product_ref + ' Doesn\'t Found'})
                            log_data.sudo().write({'product_image_upload_line_ids': [(4, log_line.id)]})
                            return Response(json.dumps({'success': False, 'msg': 'Product Doesnot Found'}),
                                            content_type='application/json',
                                            status=400)

                    return Response(json.dumps({'success': True, 'msg': 'Image Uploaded Successufully'}),
                                    content_type='application/json',
                                    status=200)
            else:
                existing_folder_log = request.env['folder.update.log'].sudo().search([('folder_path', '=', dir_path)],
                                                                                     order="root_modified_date desc",
                                                                                     limit=1)
                if not existing_folder_log:
                    request.env['folder.update.log'].sudo().create(
                        {'root_path': root_path, 'folder_path': dir_path, 'modified_date': file_latest_time_stamp,
                         'root_modified_date': datetime.datetime.now()})
                    return Response(json.dumps({'success': False, 'msg': 'Product Doesnot Found'}),
                                    content_type='application/json',
                                    status=400)
                else:
                    existing_folder_log.sudo().write(
                        {'modified_date': file_latest_time_stamp, 'root_modified_date': datetime.datetime.now()})
                    return Response(json.dumps({'success': False, 'msg': 'Product Doesnot Found'}),
                                    content_type='application/json',
                                    status=400)
        except Exception as e:
            return Response(json.dumps({'success': False, 'msg': str(e)}),
                            content_type='application/json',
                            status=500)
