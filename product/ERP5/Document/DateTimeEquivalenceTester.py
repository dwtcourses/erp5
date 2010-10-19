# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
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

import zope.interface
from AccessControl import ClassSecurityInfo
from DateTime import DateTime

from Products.ERP5Type.Core.Predicate import Predicate
from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5.mixin.equivalence_tester import EquivalenceTesterMixin

class DateTimeEquivalenceTester(Predicate, EquivalenceTesterMixin):
  """
  The purpose of this divergence tester is to check the
  consistency between delivery movement and simulation movement
  for some specific properties.
  """
  meta_type = 'ERP5 DateTime Equivalence Tester'
  portal_type = 'DateTime Equivalence Tester'
  add_permission = Permissions.AddPortalContent

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = (
    PropertySheet.Base,
    PropertySheet.XMLObject,
    PropertySheet.CategoryCore,
    PropertySheet.DublinCore,
    PropertySheet.EquivalenceTester,
    PropertySheet.SolverSelection
    )

  # Declarative interfaces
  zope.interface.implements(interfaces.IEquivalenceTester,)

  def _compare(self, prevision_movement, decision_movement):
    """
    If prevision_movement and decision_movement don't match, it returns a
    list : (prevision_value, decision_value, message, mapping)
    """
    tested_property = self.getTestedProperty()
    if getattr(decision_movement, 'isPropertyRecorded',
               lambda x:False)(tested_property):
      decision_value = decision_movement.getRecordedProperty(tested_property)
    else:
      decision_value = decision_movement.getProperty(tested_property) or DateTime(0)
    prevision_value = prevision_movement.getProperty(tested_property) or DateTime(0)

    delta = decision_value - prevision_value
    # XXX we should use appropriate property sheets and getter methods
    # for these properties.
    absolute_tolerance_min = self.getProperty('quantity_range_min') or \
                             self.getProperty('quantity')
    if absolute_tolerance_min is not None and \
       delta < absolute_tolerance_min:
      return (
        prevision_value, decision_value,
        'The difference of ${property_name} between decision and prevision is less than ${value}.',
        dict(property_name=tested_property,
             value=absolute_tolerance_min))
    absolute_tolerance_max = self.getProperty('quantity_range_max') or \
                             self.getProperty('quantity')
    if absolute_tolerance_max is not None and \
       delta > absolute_tolerance_max:
      return (
        prevision_value, decision_value,
        'The difference of ${property_name} between decision and prevision is larger than ${value}.',
        dict(property_name=tested_property,
             value=absolute_tolerance_max))

  def getUpdatablePropertyDict(self, prevision_movement, decision_movement):
    """
    Returns a list of properties to update on decision_movement
    prevision_movement so that next call to compare returns True.

    prevision_movement -- a simulation movement (prevision)

    decision_movement -- a delivery movement (decision)
    """
    tested_property = self.getTestedProperty()
    prevision_value = prevision_movement.getProperty(tested_property)
    return {tested_property:prevision_value}
