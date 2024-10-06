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
        const collegeName = $('#collegeName').val();

        // Hide the warning initially
        $('#collegeCodeWarning').css('display', 'none'); // Change this line

        $.ajax({
            type: 'POST',
            url: '/create_college',
            contentType: 'application/json',
            data: JSON.stringify({
                college_code: collegeCode,
                college_name: collegeName
            }),
            success: function (response) {
                location.reload();
            },
            error: function (xhr) {
                if (xhr.status === 400) {
                    $('#collegeCodeWarning').css('display', 'block'); // Change this line
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
                url: '/check_duplicate_college_code', // Ensure this URL is correct
                type: 'POST',
                contentType: 'application/json', // Send data as JSON
                data: JSON.stringify({
                    college_code: currentCode
                }), // Stringify the data
                success: function (response) {
                    if (response.exists) {
                        $('#duplicateCollegeCodeWarning').show(); // Show duplicate warning
                    } else {
                        $('#duplicateCollegeCodeWarning').hide(); // Hide duplicate warning
                    }
                },
                error: function () {
                    // Handle error if needed
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

        // Show the warning if the code is a duplicate before updating
        if (collegeCode !== originalCollegeCode) {
            $.ajax({
                url: '/check_duplicate_college_code',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({
                    college_code: collegeCode
                }),
                success: function (response) {
                    if (response.exists) {
                        $('#duplicateCollegeCodeWarning').show(); // Show duplicate warning
                    } else {
                        proceedToUpdate(collegeCode, collegeName, originalCollegeCode); // Proceed if no duplicate
                    }
                }
            });
        } else {
            proceedToUpdate(collegeCode, collegeName, originalCollegeCode); // Proceed if no change
        }
    });

    // Function to handle the update
    function proceedToUpdate(collegeCode, collegeName, originalCollegeCode) {
        $.ajax({
            type: 'POST',
            url: '/update_college',
            contentType: 'application/json',
            data: JSON.stringify({
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
    }


    /// Delete College
    $(document).on('click', '.delete-btn', function () {
        const collegeCode = $(this).data('id');
        const collegeName = $(this).data('name');

        console.log('College Code:', collegeCode); // Debugging log
        console.log('College Name:', collegeName); // Debugging log

        $('#collegeId').text(collegeCode);
        $('#collegeName').text(collegeName);
    });

    // Confirm Deletion
    $('#confirmDeleteBtn').on('click', function () {
        const collegeCode = $('#collegeId').text();

        $.ajax({
            type: 'DELETE',
            url: '/delete_college',
            contentType: 'application/json',
            data: JSON.stringify({
                college_code: collegeCode
            }),
            success: function (response) {
                location.reload();
            },
            error: function (xhr) {
                // Handle any errors here
            }
        });
    });

});