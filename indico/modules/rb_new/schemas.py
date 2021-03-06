# This file is part of Indico.
# Copyright (C) 2002 - 2018 European Organization for Nuclear Research (CERN).
#
# Indico is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 3 of the
# License, or (at your option) any later version.
#
# Indico is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Indico; if not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

from flask import session
from marshmallow.fields import Boolean, Function, Nested, String

from indico.core.marshmallow import mm
from indico.modules.rb.models.aspects import Aspect
from indico.modules.rb.models.blocked_rooms import BlockedRoom
from indico.modules.rb.models.blocking_principals import BlockingPrincipal
from indico.modules.rb.models.blockings import Blocking
from indico.modules.rb.models.locations import Location
from indico.modules.rb.models.reservation_occurrences import ReservationOccurrence
from indico.modules.rb.models.reservations import Reservation
from indico.modules.rb.models.room_attributes import RoomAttributeAssociation
from indico.modules.rb.models.room_bookable_hours import BookableHours
from indico.modules.rb.models.room_nonbookable_periods import NonBookablePeriod
from indico.modules.rb.models.rooms import Room
from indico.modules.users.schemas import UserSchema


_room_fields = ('id', 'name', 'capacity', 'building', 'floor', 'number', 'is_public', 'location_name', 'has_vc',
                'has_projector', 'has_webcast_recording', 'full_name', 'comments', 'division', 'is_reservable',
                'is_auto_confirm', 'sprite_position')


class RoomAttributesSchema(mm.ModelSchema):
    title = String(attribute='attribute.title')

    class Meta:
        model = RoomAttributeAssociation
        fields = ('value', 'title')


class RoomSchema(mm.ModelSchema):
    owner_name = String(attribute='owner.full_name')

    class Meta:
        model = Room
        fields = _room_fields + ('surface_area', 'latitude', 'longitude', 'telephone', 'key_location',
                                 'max_advance_days', 'owner_name')


class AspectSchema(mm.ModelSchema):
    class Meta:
        model = Aspect
        fields = ('name', 'top_left_latitude', 'top_left_longitude', 'bottom_right_latitude', 'bottom_right_longitude',
                  'default_on_startup')


class ReservationSchema(mm.ModelSchema):
    class Meta:
        model = Reservation
        fields = ('id', 'booking_reason', 'booked_for_name')


class ReservationOccurrenceSchema(mm.ModelSchema):
    reservation = Nested(ReservationSchema)

    class Meta:
        model = ReservationOccurrence
        fields = ('start_dt', 'end_dt', 'is_valid', 'reservation')


class BlockedRoomSchema(mm.ModelSchema):
    room = Nested(RoomSchema, only=('id', 'name', 'sprite_position', 'full_name'))

    class Meta:
        model = BlockedRoom
        fields = ('rejection_reason', 'room')


class BlockingPrincipalSchema(mm.ModelSchema):
    identifier = Function(lambda blocking_principal: blocking_principal.identifier)
    full_name = String()
    provider = String(missing=None)
    email = String(missing=None)
    is_group = Boolean(missing=False)

    class Meta:
        model = BlockingPrincipal
        fields = ('id', 'identifier', 'name', 'is_group', 'email', 'full_name', 'provider')


class BlockingSchema(mm.ModelSchema):
    blocked_rooms = Nested(BlockedRoomSchema, many=True)
    allowed = Nested(BlockingPrincipalSchema, many=True)
    can_edit = Function(lambda blocking: blocking.can_be_modified(session.user))

    class Meta:
        model = Blocking
        fields = ('id', 'start_date', 'end_date', 'reason', 'blocked_rooms', 'allowed', 'created_by_id', 'can_edit')


class NonBookablePeriodSchema(mm.ModelSchema):
    class Meta:
        model = NonBookablePeriod
        fields = ('start_dt', 'end_dt')


class BookableHoursSchema(mm.ModelSchema):
    class Meta:
        model = BookableHours
        fields = ('start_time', 'end_time')


class LocationsSchema(mm.ModelSchema):
    rooms = Nested(RoomSchema, many=True, only=('id', 'name', 'full_name', 'sprite_position'))

    class Meta:
        model = Location
        fields = ('id', 'name', 'rooms')


class RBUserSchema(UserSchema):
    has_owned_rooms = mm.Method('has_managed_rooms')
    favorite_users = Nested(UserSchema, many=True)

    class Meta:
        fields = UserSchema.Meta.fields + ('has_owned_rooms', 'favorite_users', 'is_admin')

    def has_managed_rooms(self, user):
        from indico.modules.rb_new.operations.rooms import has_managed_rooms
        return has_managed_rooms(user)


rb_user_schema = RBUserSchema()
rooms_schema = RoomSchema(many=True, only=_room_fields)
room_details_schema = RoomSchema()
room_attributes_schema = RoomAttributesSchema(many=True)
aspects_schema = AspectSchema(many=True)
reservation_occurrences_schema = ReservationOccurrenceSchema(many=True)
reservation_schema = ReservationSchema()
blockings_schema = BlockingSchema(many=True)
simple_blockings_schema = BlockingSchema(many=True, only=('id', 'reason'))
nonbookable_periods_schema = NonBookablePeriodSchema(many=True)
bookable_hours_schema = BookableHoursSchema()
locations_schema = LocationsSchema(many=True)
