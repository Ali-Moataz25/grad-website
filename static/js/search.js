document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.getElementById('searchFilterForm');
    const serviceTypeInput = document.getElementById('serviceTypeInput');
    const locationFilter = document.getElementById('locationFilter');
    const priceFilter = document.getElementById('priceFilter');
    const dateFilter = document.getElementById('dateFilter');
    
    // Parse the locations data from the hidden input
    const locationsData = JSON.parse(document.getElementById('locationsData').value);

    // Function to update location dropdown based on selected service type
    function updateLocationDropdown(serviceType) {
        locationFilter.innerHTML = ''; // Clear existing options
        
        if (!serviceType) {
            locationFilter.disabled = true;
            locationFilter.innerHTML = '<option value="">Select Service First</option>';
            return;
        }

        const locations = locationsData[serviceType] || [];
        locationFilter.disabled = false;

        // Add default option
        const defaultOption = document.createElement('option');
        defaultOption.value = '';
        defaultOption.textContent = locations.length ? 'All Locations' : 'No Locations Available';
        locationFilter.appendChild(defaultOption);

        // Add location options
        locations.forEach(location => {
            const option = document.createElement('option');
            option.value = location;
            option.textContent = location;
            locationFilter.appendChild(option);
        });
    }

    // Listen for service type changes
    serviceTypeInput.addEventListener('change', function() {
        updateLocationDropdown(this.value);
    });

    searchForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Check if service type is selected
        if (!serviceTypeInput.value) {
            alert('Please select a service type');
            return;
        }

        // Build the query parameters
        const params = new URLSearchParams();
        
        if (locationFilter.value) {
            params.append('location', locationFilter.value);
        }
        
        if (priceFilter.value) {
            params.append('max_price', priceFilter.value);
        }
        
        if (dateFilter.value) {
            params.append('date', dateFilter.value);
        }

        // Redirect to the specific service page with filters
        const queryString = params.toString() ? `?${params.toString()}` : '';
        window.location.href = `/services/${serviceTypeInput.value}${queryString}`;
    });

    // Optional: Add filter functionality
    [locationFilter, priceFilter, dateFilter].forEach(filter => {
        filter.addEventListener('change', function() {
            // You can add live filtering here if needed
            // For now, we'll just use the form submission
        });
    });
}); 