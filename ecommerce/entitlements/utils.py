from __future__ import unicode_literals

import logging

from django.conf import settings
from django.db.models import Q
from oscar.core.loading import get_model

from ecommerce.core.constants import COURSE_ENTITLEMENT_PRODUCT_CLASS_NAME
from ecommerce.extensions.catalogue.utils import generate_sku

logger = logging.getLogger(__name__)
Category = get_model('catalogue', 'Category')
Product = get_model('catalogue', 'Product')
ProductCategory = get_model('catalogue', 'ProductCategory')
ProductClass = get_model('catalogue', 'ProductClass')
StockRecord = get_model('partner', 'StockRecord')


def create_parent_course_entitlement(name, UUID):
    """ Create the parent course entitlement product if it does not already exist. """
    parent, created = Product.objects.get_or_create(
        structure=Product.PARENT,
        product_class=ProductClass.objects.get(name=COURSE_ENTITLEMENT_PRODUCT_CLASS_NAME),
        attributes__name='UUID',
        attribute_values__value_text=UUID,
        defaults={
            'title': 'Parent Course Entitlement for {}'.format(name),
            'is_discountable': True,
        },
    )
    parent.attr.UUID = UUID
    parent.attr.save()

    if created:
        logger.debug('Created new parent course_entitlement [%d] for [%s].', parent.id, UUID)
    else:
        logger.debug('Parent course_entitlement [%d] already exists for [%s].', parent.id, UUID)

    ProductCategory.objects.get_or_create(category=Category.objects.get(name='Course Entitlements'), product=parent)

    return parent, created


def get_entitlement(uuid, certificate_type):
    """ Get a Course Entitlement Product """
    uuid_query = Q(
        attributes__name='UUID',
        attribute_values__value_text=unicode(uuid),
    )
    certificate_type_query = Q(
        attributes__name='certificate_type',
        attribute_values__value_text=certificate_type.lower(),
    )
    return Product.objects.filter(uuid_query).get(certificate_type_query)


def create_or_update_course_entitlement(certificate_type, price, partner, UUID, name, id_verification_required=False):
    """ Create or Update Course Entitlement Products """
    certificate_type = certificate_type.lower()
    UUID = unicode(UUID)

    try:
        parent_entitlement, __ = create_parent_course_entitlement(name, UUID)
        course_entitlement = get_entitlement(UUID, certificate_type)
    except Product.DoesNotExist:
        course_entitlement = Product()

    course_entitlement.structure = Product.CHILD
    course_entitlement.is_discountable = True
    course_entitlement.title = 'Course {}'.format(name)
    course_entitlement.attr.certificate_type = certificate_type
    course_entitlement.attr.UUID = UUID
    course_entitlement.attr.id_verification_required = id_verification_required
    course_entitlement.parent = parent_entitlement
    course_entitlement.save()

    sku = generate_sku(course_entitlement, partner)
    __, created = StockRecord.objects.update_or_create(
        product=course_entitlement, partner=partner,
        defaults={
            'product': course_entitlement,
            'partner': partner,
            'partner_sku': sku,
            'price_excl_tax': price,
            'price_currency': settings.OSCAR_DEFAULT_CURRENCY,
        }
    )

    if created:
        logger.info(
            'Course entitlement product stock record with certificate type [%s] for [%s] does not exist. '
            'Instantiated a new instance.',
            certificate_type,
            UUID
        )

    return course_entitlement, sku
