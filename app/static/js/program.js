$(document).ready(function () {
    // Initialize DataTable
    const programTable = $('#program_table').DataTable({
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

    // Function to validate the create form
    function validateCreateForm() {
        const courseCode = $('#courseCode').val().trim();
        const courseName = $('#courseName').val().trim();
        const college = $('#college').val();
        const hasDuplicate = $('#courseCodeWarning').is(':visible');

        const isValid = courseCode !== '' && courseName !== '' && college !== '' && !hasDuplicate;
        $('#createProgramBtn').prop('disabled', !isValid);
    }

    // Validate form on input change
    $('#createProgramForm input, #createProgramForm select').on('input change', validateCreateForm);

    // Check for duplicate course code
    $('#courseCode').on('input', function() {
        const courseCode = $(this).val().trim();
        if (courseCode === '') {
            $('#courseCodeWarning').hide();
            validateCreateForm();
            return;
        }

        $.ajax({
            url: '/check_course_code',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ course_code: courseCode }),
            success: function(response) {
                if (response.exists) {
                    $('#courseCodeWarning').show();
                } else {
                    $('#courseCodeWarning').hide();
                }
                validateCreateForm();
            }
        });
    });

    // Create program functionality
    $('#createProgramForm').submit(function(e) {
        e.preventDefault();
        const courseCode = $('#courseCode').val().trim();
        const courseName = $('#courseName').val().trim();
        const college = $('#college').val();

        $.ajax({
            url: '/programs',
            method: 'POST',
            data: {
                courseCode: courseCode,
                courseName: courseName,
                college: college
            },
            success: function(response) {
                $('#createModal').modal('hide');
                location.reload();  // Reload the page to show the new program
            },
            error: function(xhr) {
                if (xhr.status === 400) {
                    $('#courseCodeWarning').show();
                    validateCreateForm();
                }
            }
        });
    });

    // Edit program functionality
    $(document).on('click', '.edit-btn', function () {
        const courseCode = $(this).data('id');
        const courseName = $(this).data('name');
        const college = $(this).data('college');

        $('#editCourseCode').val(courseCode);
        $('#editCourseName').val(courseName);
        $('#editCollege').val(college);
        $('#originalCourseCode').val(courseCode);

        // Hide warning initially
        $('#courseCodeWarning').hide();

        $('#editModal').modal('show');
    });

    // Show warning only when course code is changed
    $('#editCourseCode').on('input', function () {
        const originalCode = $('#originalCourseCode').val();
        if ($(this).val() !== originalCode) {
            $('#courseCodeWarning').show();
        } else {
            $('#courseCodeWarning').hide();
        }
    });

    // Revert course code
    $('#revertLink').click(function (e) {
        e.preventDefault();
        const originalCode = $('#originalCourseCode').val();
        $('#editCourseCode').val(originalCode);
        $('#courseCodeWarning').hide();
    });

    // Update program
    $('#updateProgramBtn').click(function () {
        const originalCourseCode = $('#originalCourseCode').val();
        const courseCode = $('#editCourseCode').val();
        const courseName = $('#editCourseName').val();
        const college = $('#editCollege').val();

        // Validate college dropdown
        if (college === "") {
            alert('Course must belong to a college.');
            return; // Prevent form submission
        }

        $.ajax({
            url: '/programs/update',
            method: 'POST',
            data: {
                originalCourseCode: originalCourseCode,
                courseCode: courseCode,
                courseName: courseName,
                college: college
            },
            success: function (response) {
                if (response.success) {
                    $('#editModal').modal('hide');
                    // Update the table row
                    const row = programTable.row($(`button[data-id="${originalCourseCode}"]`).closest('tr'));
                    const newData = [
                        courseCode,
                        courseName,
                        college,
                        `<button class="btn btn-warning btn-sm edit-btn" data-bs-toggle="modal" data-bs-target="#editModal" data-id="${courseCode}" data-name="${courseName}" data-college="${college}">
                            <i class="fas fa-edit p-1"></i>
                        </button>`,
                        `<button class="btn btn-danger btn-sm delete-btn" data-bs-toggle="modal" data-bs-target="#deleteModal" data-id="${courseCode}" data-name="${courseName}">
                            <i class="fas fa-trash p-1"></i>
                        </button>`
                    ];
                    row.data(newData).draw();
                } else {
                    alert('Failed to update program: ' + response.message);
                }
            },
            error: function () {
                alert('An error occurred while updating the program');
            }
        });
    });

    // Delete program functionality
    $(document).on('click', '.delete-btn', function () {
        const courseCode = $(this).data('id');
        const courseName = $(this).data('name');

        $('#programName').text(courseName);
        $('#programId').text(courseCode);
        $('#deleteModal').modal('show');
    });

    // Confirm delete
    $('#confirmDeleteBtn').click(function () {
        const courseCode = $('#programId').text();

        $.ajax({
            url: `/programs/delete/${courseCode}`,
            method: 'DELETE',
            success: function (response) {
                if (response.message === "Program deleted successfully") {
                    $('#deleteModal').modal('hide');
                    // Remove the row from the DataTable
                    programTable.row($(`button[data-id="${courseCode}"]`).closest('tr')).remove().draw();
                } else {
                    alert('Failed to delete program: ' + response.message);
                }
            },
            error: function (xhr, status, error) {
                alert('An error occurred while deleting the program: ' + error);
            }
        });
    });

    // Check for duplicate course code
    $('#courseCode').on('input', function() {
        const courseCode = $(this).val();
        $.ajax({
            url: '/check_course_code',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ course_code: courseCode }),
            success: function(response) {
                if (response.exists) {
                    $('#courseCodeWarning').show();
                } else {
                    $('#courseCodeWarning').hide();
                }
            }
        });
    });
});