$(document).ready(function () {
    // Initialize DataTable
    const programTable = $('#college_table').DataTable({
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
        $('#collegeCodeWarning').hide();

        $.ajax({
            type: 'POST',
            url: '/create_college',
            data: {
                collegeCode: collegeCode,
                collegeName: collegeName
            },
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
});