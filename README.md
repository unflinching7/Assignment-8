## Product Business to	Service	Business Renamings:

_allocations	    to	_reservations

_purchased_quantity	to slot_qty	                    

allocate	        to	reserve_slot

allocated_quantity	to	reserved_quantity

allocations	        to	reservations

Batch	            to	AppointmentSlot

batches	            to	appointment_slots

batchref	        to	slot_ref

can_allocate	    to	can_reserve

deallocate	        to	cancel_reservation

eta	                to	start_time

insert_batch	    to	insert_slot

InvalidSku	        to	InvalidServiceType

order_lines	        to	check_in_requests

order_lines.id	    to	check_in_request.id

orderid	            to	requestid

OrderLine	        to	CheckInRequest

orderline_id	    to	checkinrequest_id

OutOfStock	        to	NoAvailableSlots

product	            to	service_offering

Product	            to	ServiceOffering

qty	                to	availability

reference	        to	slot_reference

sku	                to	service_type	(existing/new)

version_number	    to	location_number	


## Problem in a _Chiropractic_ Practice

A complexity faced by a chiropractic practice with multiple locations is long wait times for customers due to variations in demand and appointment lengths.  This leads to customer frustration and lost business. As a solution, the practice should implement a system that allows customers to check-in via an app and receive real-time updates on wait times at the selected location.

To achieve this, the corporate management team will still be responsible for hiring and scheduling chiropractors for each location based on appointment demand.  They will however benefit from the tracking provided by the new system regarding demand fluctuations. The current Scheduling system will assign and schedule chiropractors to each location and notify the Reservation system about their schedules. The Reservation system will reserve available slots for customer check-in requests and send reservation details to the location office.

The new Ecommerce system will respond to check-in requests made by customers via the app and provide them with check-in reservations.  It will ask the Reservation system for wait times and notify the Reservation system about the check-in request.

Even before the customer arrives at the location, they can use the app to check-in and reserve a slot for chiropractic service, if they can be there in person on time. The Reservation system allocates the available slot and sends the reservation details to the location office. It follows business rules of reserving two slots for each new customer and one slot per existing customer.  Also, if the wait time equals or exceeds 45 minutes the system will not reserve slots and respond with a message that there is no slot availability.  The customer receives updates on the wait time via the app and can use that waiting time for driving to the location.  When a chiropractor is available, the location office provides the service to the customer and uses the Payment system to process the payment.

The chiropractor delivers the service at the location to customers with walk-in reservations on an as checked in basis and according to the business rules.  The system ensures that business rules are followed by assigning chiropractors based on appointment demand and scheduling them accordingly.

Implementing a system that allows customers to check-in and receive real-time updates on wait times can significantly reduce wait times at this a chiropractic practice with multiple locations.  By automating the process of managing check-in reservations and scheduling based on requested demand, the system can efficiently allocate resources and reduce customer frustration, leading to increased business profits and customer satisfaction.
