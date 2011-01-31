##############################################################################
#
# Copyright (c) 2011 Nexedi SARL and Contributors. All Rights Reserved.
#                    Nicolas Dumazet <nicolas.dumazet@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################
"""
This module should include most code related to the generation of
Accessor Holders, that is, generation of methods for ERP5

* Ideally, PropertyHolder class should be defined here, as well
as a base class for all erp5.accessor_holder Accessor Holders.
* Utils, Property Sheet Tool can be probably be cleaned up as well by
moving specialized code here.
"""
from Products.ERP5Type.Base import PropertyHolder
from Products.ERP5Type.Utils import createRelatedAccessors, createExpressionContext

generating_base_accessors = False
def _generateBaseAccessorHolder(portal,
    property_sheet_tool, accessor_holder_module):
  base_accessor_holder_id = 'BaseAccessorHolder'

  accessor_holder = getattr(accessor_holder_module,
                            base_accessor_holder_id,
                            None)
  if accessor_holder is not None:
    return accessor_holder

  global generating_base_accessors
  if generating_base_accessors:
    # can cause recursion, as accessing categories generates category properties
    return None
  generating_base_accessors = True

  portal_categories = getattr(portal, 'portal_categories', None)
  if portal_categories is None:
    generating_base_accessors = False
    return None

  base_category_list = portal_categories.objectIds()

  property_holder = PropertyHolder()

  econtext = createExpressionContext(portal, portal)
  createRelatedAccessors(portal_categories,
                         property_holder,
                         econtext,
                         base_category_list)

  accessor_holder = property_sheet_tool._createCommonPropertySheetAccessorHolder(
                      property_holder,
                      base_accessor_holder_id,
                      'erp5.accessor_holder',
                      skip_default=True)
  setattr(accessor_holder_module, base_accessor_holder_id, accessor_holder)
  generating_base_accessors = False
  return accessor_holder

def _generatePreferenceToolAccessorHolder(accessor_holder_list,
    property_sheet_tool, accessor_holder_module):
  property_holder = PropertyHolder()

  from Products.ERP5Type.Accessor.TypeDefinition import list_types
  from Products.ERP5Type.Utils import convertToUpperCase
  from Products.ERP5Form.PreferenceTool import PreferenceMethod

  for accessor_holder in accessor_holder_list:
    for prop in accessor_holder._properties:
      if prop.get('preference'):
        # XXX read_permission and write_permissions defined at
        # property sheet are not respected by this.
        # only properties marked as preference are used
        attribute = prop['id']
        attr_list = [ 'get%s' % convertToUpperCase(attribute)]
        if prop['type'] == 'boolean':
          attr_list.append('is%s' % convertToUpperCase(attribute))
        if prop['type'] in list_types :
          attr_list.append('get%sList' % convertToUpperCase(attribute))
        read_permission = prop.get('read_permission')
        for attribute_name in attr_list:
          method = PreferenceMethod(attribute_name, prop.get('default'))
          setattr(property_holder, attribute_name, method)
          if read_permission:
            property_holder.declareProtected(read_permission, attribute_name)

  accessor_holder = property_sheet_tool._createCommonPropertySheetAccessorHolder(
                      property_holder,
                      'PreferenceTool',
                      'erp5.accessor_holder',
                      skip_default=True)
  setattr(accessor_holder_module, 'PreferenceTool', accessor_holder)
  return accessor_holder

