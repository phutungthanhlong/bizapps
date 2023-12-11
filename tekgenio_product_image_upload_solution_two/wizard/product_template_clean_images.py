from odoo import models, fields


class CleanExtaImagesWizard(models.TransientModel):
    _name = "clean.extra.images.wizard"

    name = fields.Char(string="Enter Image Names", required=True)
    product_tmpl_ids = fields.Char("Product Templates")

    def delete_the_extra_images(self):
        if self.name and self.product_tmpl_ids:
            images_to_delete = [name.strip() for name in self.name.split(',')]
            product_ids_str = self.product_tmpl_ids.strip('[]')
            product_ids = [int(product_id) for product_id in product_ids_str.split(',')]

            # Fetch products from Odoo based on the provided product IDs
            products = self.env['product.template'].browse(product_ids)

            for product in products:
                # Check if the product has images and delete the specified ones
                if product.product_template_image_ids:
                    for image in product.product_template_image_ids.filtered(lambda rec: rec.name in images_to_delete):
                        image.unlink()
        else:
            pass
