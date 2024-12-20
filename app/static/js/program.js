$(document).ready(function () {
    // Initialize DataTable
    const programTable = $('#program_table').DataTable({
        columnDefs: [
            {
                orderable: false,
                targets: [-3]
            },
            {
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
                validateCreateForm(); // Re-validate the form after checking for duplicates
            }
        });
    });
    $('#courseCode, #editCourseCode').on('blur', function() {
        const courseCode = $(this).val();
        const warningElement = $(this).closest('.modal-body').find('#courseCodeWarning');
        const submitButton = $(this).closest('form').find('button[type="submit"]');
        
        fetch(`/programs/check_course_code`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ course_code: courseCode }),
        })
        .then(response => response.json())
        .then(data => {
            const isDuplicate = data.exists;
            warningElement.toggle(isDuplicate);
            submitButton.prop('disabled', isDuplicate);
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

        // Fetch enrolled students
        $.ajax({
            url: `/programs/${courseCode}/students`,
            method: 'GET',
            success: function (response) {
            const students = response.students;
            const formattedStudentList = students.map(student => `<div>${student.name}</div>`).join('');
            $('#deleteModal .modal-body').html(`
                <p>Deleting <strong>${courseName} (${courseCode})</strong> will also unenroll the following students (${students.length} total):</p>
                ${formattedStudentList}
                </br>
                <p><strong>Proceed?</strong></p>
            `).css('margin-top', '20px');
            },
            error: function(xhr, status, error) {
                console.error('Error fetching students:', error);
                $('#deleteModal .modal-body').html(`
                    <p class="text-danger">Error loading students</p>
                `);
            }
        });
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

    // Info modal functionality
    $(document).on('click', '.info-btn', function () {
        const courseCode = $(this).data('id');
        const courseName = $(this).data('name');
        const college = $(this).data('college');

        // Reset modal content
        $('#infoCourseCode').text(courseCode);
        $('#infoCourseName').text(courseName);
        $('#infoCollege').text(college);
        $('#infoEnrolledStudents').empty();

        // Fetch enrolled students
        $.ajax({
            url: `/programs/${courseCode}/students`,
            method: 'GET',
            success: function (response) {
                const students = response.students;
                const yearLevels = response.year_levels;

                // Container for student count and "See enrolled" link
                const enrollmentContainer = $('<div>').addClass('d-flex align-items-center gap-2');
                
                // Add student count
                enrollmentContainer.append($('<span>').text(`${students.length} students`));
                
                // Add "See enrolled" link if there are students
                if (students.length > 0) {
                    const seeEnrolledLink = $('<a>')
                        .attr('href', '#')
                        .addClass('see-enrolled-link')
                        .text('See enrolled')
                        .click(function(e) {
                            e.preventDefault();
                            showStudentList(students);
                        });
                    enrollmentContainer.append(seeEnrolledLink);
                }
                
                $('#infoEnrolledStudents').append(enrollmentContainer);

                // Display pie chart
                displayYearLevelPieChart(yearLevels);
            },
            error: function(xhr, status, error) {
                console.error('Error fetching students:', error);
                $('#infoEnrolledStudents').append(
                    $('<div>').addClass('text-danger').text('Error loading students')
                );
            }
        });

        $('#infoModal').modal('show');
    });

    function showStudentList(students) {
        // Create student list container
        const studentListContainer = $('<div>')
            .attr('id', 'studentList')
            .addClass('mt-3');

        // Add back button
        const backButton = $('<button>')
            .addClass('btn btn-sm btn-secondary mb-2')
            .text('Back to count')
            .click(function () {
                $('#studentList').remove();
                $('.see-enrolled-link').show();
            });

        studentListContainer.append(backButton);

        // Create and add student links
        const studentList = $('<div>').addClass('student-list');
        students.forEach(student => {
            studentList.append(
                $('<div>')
                    .addClass('mb-1')
                    .append(
                        $('<a>')
                            .attr('href', '#')
                            .addClass('student-link')
                            .text(student.name)
                            .click(function(e) {
                                e.preventDefault();
                                window.location.href = `/students?id=${student.id_num}`;
                            })
                    )
            );
        });

        studentListContainer.append(studentList);

        // Hide the "See enrolled" link and append the student list
        $('.see-enrolled-link').hide();
        $('#infoEnrolledStudents').append(studentListContainer);
    }

    // pie chart
    let yearLevelPieChart;

    function displayYearLevelPieChart(yearLevels) {
        const ctx = document.getElementById('yearLevelPieChart').getContext('2d');
        const labels = ['First Year', 'Second Year', 'Third Year', 'Fourth Year'];
        const data = [
            yearLevels.first_year,
            yearLevels.second_year,
            yearLevels.third_year,
            yearLevels.fourth_year
        ];

        // reset pie chart
        if (yearLevelPieChart) {
            yearLevelPieChart.destroy();
        }

        yearLevelPieChart = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: [
                        'rgba(54, 162, 235, 0.2)',
                        'rgba(75, 192, 192, 0.2)',
                        'rgba(153, 102, 255, 0.2)',
                        'rgba(255, 159, 64, 0.2)'
                    ],
                    borderColor: [
                        'rgba(54, 162, 235, 1)',
                        'rgba(75, 192, 192, 1)',
                        'rgba(153, 102, 255, 1)',
                        'rgba(255, 159, 64, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                const label = context.label || '';
                                const value = context.raw || 0;
                                return `${label}: ${value} students`;
                            }
                        }
                    }
                }
            }
        });
    }
});

