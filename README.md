Product Busines to	Service	Business Renamings:

_allocations	to	_reservations

_purchased_quantity	to slot_qty	                    (can be more than 1, such as parent and child)

allocate	to	reserve_slot

allocated_quantity	to	reserved_quantity

allocations	to	reservations

Batch	to	AppointmentSlot

batches	to	appointment_slots

batchref	to	slot_ref

can_allocate	to	can_reserve

deallocate	to	cancel_reservation

eta	to	start_time

insert_batch	to	insert_slot

InvalidSku	to	InvalidServiceType

order_lines	to	check_in_requests

order_lines.id	to	check_in_request.id

orderid	to	requestid

OrderLine	to	CheckInRequest

orderline_id	to	checkinrequest_id

OutOfStock	to	NoAvailableSlots

product	to	service_offering

Product	to	ServiceOffering

qty	to	availability

reference	to	slot_reference

sku	to	service_type	(repeat, new which requires double slot)

version_number	to	location_number	