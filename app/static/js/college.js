$(document).ready(function () {
    const collegeTable = initializeDataTable();
    setupCreateCollegeForm();
    setupCollegeCodeValidation();
    setupEditCollege();
    setupDeleteCollege();
    setupInfoButton();
});

function initializeDataTable() {
    return $('#college_table').DataTable({
        columnDefs: [
            { orderable: false, targets: [-3, -2, -1] }
        ],
        initComplete: function () {
            $('.dataTables_filter input').attr('placeholder', 'Search...');
        }
    });
}

function setupCreateCollegeForm() {
    $('#createCollegeForm').on('submit', function (event) {
        event.preventDefault();
        const collegeCode = $('#collegeCode').val();
        const collegeName = $('#collegeName').val();
        $('#collegeCodeWarning').hide();

        $.ajax({
            type: 'POST',
            url: '/colleges/create',
            contentType: 'application/json',
            data: JSON.stringify({ college_code: collegeCode, college_name: collegeName }),
            success: function () { location.reload(); },
            error: function (xhr) { 
                if (xhr.status === 400) { $('#collegeCodeWarning').show(); }
            }
        });
    });
}

function setupCollegeCodeValidation() {
    $('#collegeCode').on('blur', function () {
        const collegeCode = $(this).val();
        validateCollegeCode(collegeCode, function(isDuplicate) {
            $('#collegeCodeWarning').toggle(isDuplicate);
            $('#createCollegeForm button[type="submit"]').prop('disabled', isDuplicate);
        });
    });

    $('#editCollegeCode').on('input', function () {
        const currentCode = $(this).val();
        const originalCode = $('#originalCollegeCode').val();

        $('#editCollegeCodeWarning, #duplicateCollegeCodeWarning').hide();

        if (currentCode !== originalCode) {
            validateCollegeCode(currentCode, function(isDuplicate) {
                $('#duplicateCollegeCodeWarning').toggle(isDuplicate);
            });
        }
    });
}

function validateCollegeCode(collegeCode, callback) {
    $.ajax({
        url: '/colleges/check_code',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ college_code: collegeCode }),
        success: function (response) { callback(response.exists); },
        error: function () { callback(false); }
    });
}

function setupEditCollege() {
    $(document).on('click', '.edit-btn', function () {
        const collegeCode = $(this).data('id');
        const collegeName = $(this).data('name');

        $('#editCollegeCode').val(collegeCode);
        $('#editCollegeName').val(collegeName);
        $('#originalCollegeCode').val(collegeCode);
        $('#editModal').modal('show');
    });

    $('#updateCollegeBtn').on('click', function () {
        const collegeCode = $('#editCollegeCode').val();
        const collegeName = $('#editCollegeName').val();
        const originalCollegeCode = $('#originalCollegeCode').val();

        if (collegeCode !== originalCollegeCode) {
            validateCollegeCode(collegeCode, function (isDuplicate) {
                if (!isDuplicate) {
                    updateCollege(collegeCode, collegeName, originalCollegeCode);
                } else {
                    $('#duplicateCollegeCodeWarning').show();
                }
            });
        } else {
            updateCollege(collegeCode, collegeName, originalCollegeCode);
        }
    });
}

function updateCollege(collegeCode, collegeName, originalCollegeCode) {
    $.ajax({
        type: 'POST',
        url: '/colleges/update',
        contentType: 'application/json',
        data: JSON.stringify({
            college_code: collegeCode,
            college_name: collegeName,
            original_code: originalCollegeCode
        }),
        success: function () { location.reload(); },
        error: function () { alert('Error updating college. Please try again.'); }
    });
}

function setupDeleteCollege() {
    $(document).on('click', '.delete-btn', function () {
        const collegeCode = $(this).data('id');
        const collegeName = $(this).data('name');
        $('#collegeId').text(collegeCode);
        $('#collegeName').text(collegeName);

        // Fetch courses and students
        $.ajax({
            url: `/colleges/${collegeCode}/info`,
            method: 'GET',
            success: function (response) {
                const courses = response.courses;
                const totalStudents = response.total_students;
                const courseList = courses.map(course => `
                    <li>${course.course_name} (${course.course_code}): ${course.student_count} students</li>
                `).join('');

                $('#deleteModal .modal-body').html(`
                    <p>Deleting <strong>${collegeName} (${collegeCode})</strong> will also delete the following courses and unenroll the students:</p>
                    <ul>${courseList}</ul>
                    <p><strong>Total students to be unenrolled: ${totalStudents}</strong></p>
                    <p class="text-danger mt-3">Are you sure you want to proceed?</p>
                `);
            },
            error: function (xhr, status, error) {
                console.error('Error fetching college info:', error);
                $('#deleteModal .modal-body').html(`
                    <p class="text-danger">Error loading courses and students</p>
                `);
            }
        });

        $('#deleteModal').modal('show');
    });

    $('#confirmDeleteBtn').on('click', function () {
        const collegeCode = $('#collegeId').text();
        deleteCollege(collegeCode);
    });
}

function deleteCollege(collegeCode) {
    $.ajax({
        type: 'DELETE',
        url: '/colleges/delete',
        contentType: 'application/json',
        data: JSON.stringify({ college_code: collegeCode }),
        success: function () { location.reload(); },
        error: function () { alert('Error deleting college. Please try again.'); }
    });
}

// pie chart isntance
let studentPieChart;

function setupInfoButton() {
    $(document).on('click', '.info-btn', function () {
        const collegeCode = $(this).data('id');
        const collegeName = $(this).data('name');

        $('#infoCollegeCode').text(collegeCode);
        $('#infoCollegeName').text(collegeName);
        $('#infoCourses').empty();
        $('#infoStudents').empty();

        // fetch courses and students
        $.ajax({
            url: `/colleges/${collegeCode}/info`,
            method: 'GET',
            success: function (response) {
                const courses = response.courses;
                const totalStudents = response.total_students;
                const courseList = $('<ul>').addClass('list-group');

                courses.forEach(course => {
                    const courseItem = $('<li>').addClass('list-group-item d-flex justify-content-between align-items-center');
                    courseItem.text(`${course.course_name} (${course.course_code})`);
                    const studentCount = $('<span>').addClass('badge bg-primary rounded-pill').text(course.student_count);
                    courseItem.append(studentCount);
                    courseList.append(courseItem);
                });

                $('#infoCourses').append(courseList);
                $('#infoTotalStudents').text(`Total Students: ${totalStudents}`);

                // Display pie chart
                displayPieChart(courses);
            },
            error: function (xhr, status, error) {
                console.error('Error fetching college info:', error);
                $('#infoCourses').append(
                    $('<div>').addClass('text-danger').text('Error loading courses')
                );
            }
        });

        $('#infoModal').modal('show');
    });
}

function displayPieChart(courses) {
    const ctx = document.getElementById('studentPieChart').getContext('2d');
    const labels = courses.map(course => course.course_name);
    const data = courses.map(course => course.student_count);

    // reset pie chart
    if (studentPieChart) {
        studentPieChart.destroy();
    }

    studentPieChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: [
                    'rgba(54, 162, 235, 0.2)',
                    'rgba(75, 192, 192, 0.2)',
                    'rgba(153, 102, 255, 0.2)',
                    'rgba(255, 159, 64, 0.2)',
                    'rgba(255, 99, 132, 0.2)',
                    'rgba(255, 206, 86, 0.2)',
                    'rgba(75, 192, 192, 0.2)',
                    'rgba(153, 102, 255, 0.2)',
                    'rgba(54, 162, 235, 0.2)',
                    'rgba(255, 159, 64, 0.2)',
                    'rgba(255, 99, 132, 0.2)',
                    'rgba(255, 206, 86, 0.2)',
                    'rgba(75, 192, 192, 0.2)',
                    'rgba(153, 102, 255, 0.2)',
                    'rgba(54, 162, 235, 0.2)'
                ],
                borderColor: [
                    'rgba(54, 162, 235, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)',
                    'rgba(255, 159, 64, 1)',
                    'rgba(255, 99, 132, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 159, 64, 1)',
                    'rgba(255, 99, 132, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)',
                    'rgba(54, 162, 235, 1)'
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
