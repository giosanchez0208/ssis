$(document).ready(function () {
    // Initialize DataTable
    const collegeTable = $('#college_table').DataTable({
        columnDefs: [{
                orderable: false,
                targets: [-2]
            },
            {
                orderable: false,
                targets: [-1]
            }
        ],
        initComplete: function (settings, json) {
            $('.dataTables_filter input')
                .filter(function () {
                    return this.name === 'search';
                })
                .attr('placeholder', 'Search...');
        }
    });

    // Create College
    $('#createCollegeForm').on('submit', function (event) {
        event.preventDefault(); // Prevent the default form submission

        const collegeCode = $('#collegeCode').val();
        const collegeName = $('#collegeName').val(); // Ensure this is set correctly

        // Hide the warning initially
        $('#collegeCodeWarning').hide();

        $.ajax({
            type: 'POST',
            url: '/create_college',
            contentType: 'application/json', // Set content type to JSON
            data: JSON.stringify({ // Stringify the data
                college_code: collegeCode,
                college_name: collegeName // Ensure this is not null
            }),
            success: function (response) {
                location.reload(); // Reloads the page to show the new college
            },
            error: function (xhr) {
                if (xhr.status === 400) { // Check for specific error code
                    $('#collegeCodeWarning').show(); // Show the warning
                }
            }
        });
    });

    // Edit College
    $(document).on('click', '.edit-btn', function () {
        const collegeCode = $(this).data('id');
        const collegeName = $(this).data('name');

        $('#editCollegeCode').val(collegeCode);
        $('#editCollegeName').val(collegeName);
        $('#originalCollegeCode').val(collegeCode);
        $('#editCollegeCodeWarning').hide(); // Hide initial warning
        $('#duplicateCollegeCodeWarning').hide(); // Hide duplicate warning
    });

    $('#editCollegeCode').on('input', function () {
        const currentCode = $(this).val();
        const originalCode = $('#originalCollegeCode').val();

        // Hide warnings initially
        $('#editCollegeCodeWarning').hide();
        $('#duplicateCollegeCodeWarning').hide();

        if (currentCode !== originalCode) {
            // Logic to check for duplicates
            $.ajax({
                url: '/check_duplicate_college_code', // Example URL
                type: 'POST',
                data: {
                    college_code: currentCode
                },
                success: function (response) {
                    if (response.exists) {
                        $('#duplicateCollegeCodeWarning').show(); // Show duplicate warning
                    } else {
                        $('#duplicateCollegeCodeWarning').hide(); // Hide duplicate warning
                    }
                }
            });
        } else {
            $('#editCollegeCodeWarning').hide(); // Hide warning if no change
        }
    });


    // Update College
    $('#updateCollegeBtn').on('click', function () {
        const collegeCode = $('#editCollegeCode').val();
        const collegeName = $('#editCollegeName').val();
        const originalCollegeCode = $('#originalCollegeCode').val();

        $.ajax({
            type: 'POST',
            url: '/update_college',
            contentType: 'application/json', // Set content type to JSON
            data: JSON.stringify({ // Stringify the data
                college_code: collegeCode,
                college_name: collegeName,
                original_code: originalCollegeCode
            }),
            success: function (response) {
                location.reload(); // Reloads the page to show updated college
            },
            error: function (xhr) {
                // Handle any errors here
            }
        });
    });

    // Delete College
    $(document).on('click', '.delete-btn', function () {
        const collegeCode = $(this).data('id');
        const collegeName = $(this).data('name');

        $('#collegeId').text(collegeCode);
        $('#collegeName').text(collegeName);
    });

    // Confirm Deletion
    $('#confirmDeleteBtn').on('click', function () {
        const collegeCode = $('#collegeId').text();

        $.ajax({
            type: 'DELETE', // Change this to DELETE
            url: '/delete_college',
            contentType: 'application/json', // Set content type to JSON
            data: JSON.stringify({ // Stringify the data
                college_code: collegeCode
            }),
            success: function (response) {
                location.reload(); // Reloads the page to show updated college list
            },
            error: function (xhr) {
                // Handle any errors here
            }
        });
    });
});