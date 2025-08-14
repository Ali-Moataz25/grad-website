function updateBookingStatus(bookingId, action) {
    if (!confirm(`Are you sure you want to ${action} this booking?`)) {
        return;
    }

    fetch(`/provider/booking/${bookingId}/${action}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(data.message);
            // Reload the page to show updated status
            location.reload();
        } else {
            alert('Error: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while updating the booking status');
    });
} 