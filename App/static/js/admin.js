document.addEventListener('DOMContentLoaded', function() {
    // Search and filter functionality
    const searchInput = document.getElementById('userSearchInput');
    const filterSelect = document.getElementById('userTypeFilter');
    const searchButton = document.getElementById('searchButton');
    const userTable = document.querySelector('#userManagementModal table tbody');

    function filterUsers() {
        const searchTerm = searchInput.value.toLowerCase();
        const filterValue = filterSelect.value;
        const rows = userTable.getElementsByTagName('tr');

        for (let row of rows) {
            const nameCell = row.cells[0];
            const emailCell = row.cells[1];
            const roleCell = row.cells[2];
            
            if (!nameCell || !emailCell || !roleCell) continue;

            const name = nameCell.textContent.toLowerCase();
            const role = roleCell.textContent.toLowerCase();
            
            // Check if row matches both search term and filter
            const matchesSearch = name.includes(searchTerm) || 
                                emailCell.textContent.toLowerCase().includes(searchTerm);
            const matchesFilter = filterValue === 'all' || role === filterValue;

            row.style.display = matchesSearch && matchesFilter ? '' : 'none';
        }
    }

    // Add event listeners for search and filter
    searchInput.addEventListener('keyup', filterUsers);
    filterSelect.addEventListener('change', filterUsers);
    searchButton.addEventListener('click', filterUsers);

    // Add search by pressing Enter
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            filterUsers();
        }
    });

    // Clear search when modal is closed
    document.getElementById('userManagementModal').addEventListener('hidden.bs.modal', function () {
        searchInput.value = '';
        filterSelect.value = 'all';
        filterUsers();
    });

    // Handle view profile button clicks
    document.querySelectorAll('.view-profile').forEach(button => {
        button.addEventListener('click', async function(e) {
            e.preventDefault();
            const userId = this.getAttribute('data-id');
            
            try {
                const response = await fetch(`/professionals/view-profile/${userId}`);
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                
                const data = await response.json();
                
                // Populate modal with professional data
                document.getElementById('profName').textContent = 
                    `${data.user.first_name} ${data.user.last_name}`;
                document.getElementById('profEmail').textContent = data.user.email;
                document.getElementById('profExperience').textContent = 
                    data.professional.experience_years || 'Not specified';
                document.getElementById('profLocation').textContent = 
                    data.professional.location_pincode || 'Not specified';
                document.getElementById('profService').textContent = 
                    data.professional.preferred_service || 'Not specified';
                document.getElementById('profRating').textContent = 
                    data.professional.rating || 'No ratings yet';
                document.getElementById('profDescription').textContent = 
                    data.professional.description || 'No description available';
                
                const verificationBadge = document.getElementById('profVerification');
                verificationBadge.textContent = data.professional.verification_status;
                verificationBadge.className = 'badge ' + 
                    (data.professional.is_verified ? 'bg-success' : 'bg-warning');

                // Show the modal (not needed since we're using data-bs-toggle)
                // const profileModal = new bootstrap.Modal(document.getElementById('professionalProfileModal'));
                // profileModal.show();
            } catch (error) {
                console.error('Error:', error);
                alert('Failed to load professional profile');
            }
        });
    });


        // Handle view profile button clicks
    // document.querySelectorAll('.view-profile').forEach(button => {
    //     button.addEventListener('click', async function (e) {
    //         e.preventDefault();
    //         const userId = this.getAttribute('data-id');
                
    //         try {
    //             const response = await fetch(`/professionals/view-docs/${userId}`);
    //             if (!response.ok) {
    //                 throw new Error('Network response was not ok');
    //             }
                    
    //             const data = await response.json();
    //         } catch (e) {
    //             console.log("ERROR LOADING DOCS IN PROF PROFILE : ", e)
    //         }
    //     });
    // })    
});

// document.getElementById('reject_professional_id').addEventListener('click', function () {
//     var rejection_prof_id = document.getElementById('reject_professional_id').innerHTML;
//     console.log("REJECTED PROF ID : ", rejection_prof_id);
//     var rejection_reason_form = document.getElementById('rejection-reason-form');
//     rejection_reason_form.attributes.action = '/reject/' + rejection_prof_id;
// })


// Simplified modal closing function
function closeProfileModal() {
    const modalElement = document.getElementById('professionalProfileModal');
    const modalInstance = bootstrap.Modal.getInstance(modalElement);
    if (modalInstance) {
        modalInstance.hide();
    }
}

// Add event listener for when modal is hidden
document.getElementById('professionalProfileModal').addEventListener('hidden.bs.modal', function () {
    // Clear the modal data when it's hidden
    document.getElementById('profName').textContent = '';
    document.getElementById('profEmail').textContent = '';
    document.getElementById('profExperience').textContent = '';
    document.getElementById('profLocation').textContent = '';
    document.getElementById('profService').textContent = '';
    document.getElementById('profRating').textContent = '';
    document.getElementById('profDescription').textContent = '';
    document.getElementById('profVerification').textContent = '';
});

function openRejectModal(professionalId) {
    // Hide approval modal first
    const approvalModal = document.getElementById('approvalModal');
    const bsApprovalModal = bootstrap.Modal.getInstance(approvalModal);
    bsApprovalModal.hide();
    
    // Show rejection modal
    setTimeout(() => {
        const rejectModal = document.getElementById(`rejectReasonModal${professionalId}`);
        const bsRejectModal = new bootstrap.Modal(rejectModal);
        bsRejectModal.show();
    }, 500);
}

function closeRejectModal(professionalId) {
    // Hide rejection modal
    const rejectModal = document.getElementById(`rejectReasonModal${professionalId}`);
    const bsRejectModal = bootstrap.Modal.getInstance(rejectModal);
    bsRejectModal.hide();
    
    // Show approval modal again
    setTimeout(() => {
        const approvalModal = document.getElementById('approvalModal');
        const bsApprovalModal = new bootstrap.Modal(approvalModal);
        bsApprovalModal.show();
    }, 500);
}

// Add event listener for when rejection modals are hidden
document.querySelectorAll('.rejection-modal').forEach(modal => {
    modal.addEventListener('hidden.bs.modal', function() {
        // Show approval modal again
        setTimeout(() => {
            const approvalModal = document.getElementById('approvalModal');
            const bsApprovalModal = new bootstrap.Modal(approvalModal);
            bsApprovalModal.show();
        }, 500);
    });
}); 