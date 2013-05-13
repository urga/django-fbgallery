from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from django.utils.translation import ugettext_lazy as _

class FBGalleryApphook(CMSApp):
    name = _("Facebook Gallery")
    urls = ["fbgallery.urls"]

apphook_pool.register(FBGalleryApphook)