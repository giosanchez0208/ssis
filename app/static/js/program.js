$(document).ready(function () {
    // Initialize DataTable
    const programTable = $('#program_table').DataTable({
        columnDefs: [
            { orderable: false, targets: [-3, -2, -1] }
        ],
        initComplete: function (settings, json) {
            $('.dataTables_filter input')
                .filter(function () {
                    return this.name === 'search';
                })
                .attr('placeholder', 'Search...');
            
            openInfoModalIfCourseCodeExists();
        }
    });

    function openInfoModalIfCourseCodeExists() {
        const urlParams = new URLSearchParams(window.location.search);
        const courseCode = urlParams.get('course_code');
        
        if (!courseCode) return;
    
        let attempts = 0;
        const maxAttempts = 20;
        
        const tryOpenModal = () => {
            const table = $('#program_table').DataTable();
            table.search(courseCode).draw();
            
            const infoButton = $(`.info-btn[data-id="${courseCode}"]`);
            
            if (infoButton.length) {
                // get the data manually
                const courseName = infoButton.data('name');
                const college = infoButton.data('college');
    
                // reset modal content first
                $('#infoCourseCode').text(courseCode);
                $('#infoCourseName').text(courseName);
                $('#infoCollege').text(college);
                $('#infoEnrolledStudents').empty();
    
                // then fetch enrolled students data
                $.ajax({
                    url: `/programs/${courseCode}/students`,
                    method: 'GET',
                    success: function (response) {
                        const students = response.students;
                        const yearLevels = response.year_levels;
    
                        // container for student count and "See enrolled" link
                        const enrollmentContainer = $('<div>').addClass('d-flex align-items-center gap-2');
                        
                        // add student count
                        enrollmentContainer.append($('<span>').text(`${students.length} students`));
                        
                        // add "See enrolled" link if there are students
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
    
                        // display pie chart
                        displayYearLevelPieChart(yearLevels);
                        
                        // show modal after data is loaded
                        $('#infoModal').modal('show');
                        
                        // clean up URL
                        const newUrl = window.location.pathname;
                        window.history.replaceState({}, '', newUrl);
                        
                        // clear the search after a delay
                        setTimeout(() => {
                            table.search('').draw();
                        }, 100);
                    },
                    error: function(xhr, status, error) {
                        console.error('Error fetching students:', error);
                        $('#infoEnrolledStudents').append(
                            $('<div>').addClass('text-danger').text('Error loading students')
                        );
                        $('#infoModal').modal('show');
                    }
                });
                
                return true;
            }
            
            attempts++;
            if (attempts < maxAttempts) {
                setTimeout(tryOpenModal, 100);
            }
            return false;
        };
    
        tryOpenModal();
    }

    // Function to validate the create form
    function validateCreateForm() {
        const courseCode = $('#courseCode').val().trim();
        const courseName = $('#courseName').val().trim();
        const college = $('#college').val();
        const hasDuplicate = $('#courseCodeWarning').is(':visible');
        const isTooLong = courseCode.length > 16;

        // Show warning if course code is too long
        if (isTooLong) {
            $('#courseCodeLengthWarning').show();
        } else {
            $('#courseCodeLengthWarning').hide();
        }

        const isValid = courseCode !== '' && courseName !== '' && college !== '' && !hasDuplicate && !isTooLong;
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
            url: '/programs/check_course_code',
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

    // Create program functionality
    $('#createProgramForm').submit(function(e) {
        e.preventDefault();
        const courseCode = $('#courseCode').val().trim();
        const courseName = $('#courseName').val().trim();
        const college = $('#college').val();

        console.log(`Submitting form data: courseCode=${courseCode}, courseName=${courseName}, college=${college}`);

        $.ajax({
            url: '/programs',
            method: 'POST',
            data: {
                courseCode: courseCode,
                courseName: courseName,
                college: college
            },
            success: function(response) {
                console.log('Program added successfully');
                $('#createModal').modal('hide');
                location.reload();  // Reload the page to show the new program
            },
            error: function(xhr) {
                console.error('Error adding program:', xhr);
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
                        `<button class="btn btn-info btn-sm info-btn" data-bs-toggle="modal" data-bs-target="#infoModal" data-id="${courseCode}" data-name="${courseName}" data-college="${college}">
                            <i class="fas fa-solid fa-info p-1" style="color: white;"></i>
                        </button>`,
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

        console.log(`Setting courseCode to: ${courseCode}`);
        
        // Set the course code in the hidden input
        $('#programId').val(courseCode);

        // Fetch enrolled students
        $.ajax({
            url: `/programs/${courseCode}/students`,
            method: 'GET',
            success: function (response) {
                const students = response.students;
                const formattedStudentList = students.map(student => `<div>${student.name}</div>`).join('');
                $('#deleteModalContent').html(`
                    <p>Are you sure you want to delete the program <strong>${courseName}</strong> (${courseCode})?</p>
                    <p>Deleting <strong>${courseName} (${courseCode})</strong> will also unenroll the following students (${students.length} total):</p>
                    ${formattedStudentList}
                    </br>
                    <p><strong>Proceed?</strong></p>
                `);
                $('#deleteModal').modal('show');
            },
            error: function(xhr, status, error) {
                console.error('Error fetching students:', error);
                $('#deleteModalContent').html(`
                    <p class="text-danger">Error loading students</p>
                `);
                $('#deleteModal').modal('show');
            }
        });
    });

    // Confirm delete
    $('#confirmDeleteBtn').click(function () {
        const courseCode = $('#programId').val();
        console.log(`Attempting to delete program with courseCode: ${courseCode}`);

        if (!courseCode) {
            console.error('Course code is empty. Cannot delete program.');
            alert('Error: Course code is empty. Cannot delete program.');
            return;
        }

        $.ajax({
            url: `/programs/delete/${courseCode}`,
            method: 'DELETE',
            success: function (response) {
                if (response.success) {
                    console.log(`Program with courseCode ${courseCode} deleted successfully`);
                    $('#deleteModal').modal('hide');
                    // Refresh the DataTable
                    programTable.row($(`button[data-id="${courseCode}"]`).closest('tr')).remove().draw();
                } else {
                    alert('Failed to delete program: ' + response.error);
                }
            },
            error: function (xhr, status, error) {
                console.error(`Error deleting program with courseCode ${courseCode}: ${error}`);
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

