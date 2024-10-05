$(document).ready(function() {
    // Initialize DataTable
    $('#program_table').DataTable({
        columnDefs: [
            { orderable: false, targets: [-2] },
            { orderable: false, targets: [-1] }
        ],
        initComplete: function(settings, json) {
            $('.dataTables_filter input')
                .filter(function() {
                    return this.name === 'search';
                })
                .attr('placeholder', 'Search...');
        }
    });

    // Validate form and control submit button state
    validateForm();

    function validateForm() {
        const submitBtn = document.getElementById('submitBtn');
        const courseCodeInput = document.getElementById('courseCode');
        const courseNameInput = document.getElementById('courseName');
        const collegeInput = document.getElementById('college');
        let isValidCourseCode = false;

        function checkFormValidity() {
            const isCourseCodeFilled = courseCodeInput.value.trim() !== '';
            const isCourseNameFilled = courseNameInput.value.trim() !== '';
            const isCollegeSelected = collegeInput.value !== '';

            submitBtn.disabled = !(isValidCourseCode && isCourseCodeFilled && isCourseNameFilled && isCollegeSelected);
        }

        // Course Code validation on blur
        courseCodeInput.addEventListener('blur', function () {
            const courseCode = this.value;
            fetch('/check_course_code', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ course_code: courseCode }),
            })
            .then(response => response.json())
            .then(data => {
                isValidCourseCode = !data.exists;
                document.getElementById('courseCodeError').style.display = data.exists ? 'block' : 'none';
                checkFormValidity();
            });
        });

        // Add input listeners to recheck form on changes
        courseCodeInput.addEventListener('input', checkFormValidity);
        courseNameInput.addEventListener('input', checkFormValidity);
        collegeInput.addEventListener('change', checkFormValidity);

        // Initial check in case of any pre-filled values
        checkFormValidity();
    }

    // Handle edit modal logic
    const editModal = document.getElementById('editModal');

    editModal.addEventListener('show.bs.modal', function (event) {
        const button = event.relatedTarget;
        const courseCode = button.getAttribute('data-id');

        fetch(`/edit_program/${courseCode}`)
            .then(response => response.json())
            .then(program => {
                document.getElementById('editCourseCode').value = program.course_code;
                document.getElementById('editCourseName').value = program.course_name;
                document.getElementById('editCollege').value = program.college;
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while fetching program data.');
            });
    });

    // Enable/disable editing of Course Code and College
    document.getElementById('enableEditCourseCode').addEventListener('change', function() {
        document.getElementById('editCourseCode').readOnly = !this.checked;
    });

    document.getElementById('enableEditCollege').addEventListener('change', function() {
        document.getElementById('editCollege').disabled = !this.checked;
    });

    // Handle edit form submission
    const editForm = document.getElementById('editForm');
    editForm.addEventListener('submit', function (e) {
        e.preventDefault();
        const formData = new FormData(this);
        const courseCode = document.getElementById('editCourseCode').value;

        fetch(`/edit_program/${courseCode}`, {
            method: 'POST',
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const modal = bootstrap.Modal.getInstance(editModal);
                modal.hide();
                location.reload();
            } else {
                alert(data.message || 'An error occurred while updating the program.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while updating the program.');
        });
    });

    // Delete modal logic
    $('#deleteModal').on('show.bs.modal', function(event) {
        var button = $(event.relatedTarget);
        var programName = button.data('program-name');
        var programId = button.data('id');
        
        var modal = $(this);
        modal.find('#programName').text(programName);
        modal.find('#programId').text(programId);
        
        modal.find('#confirmDeleteBtn').off('click').on('click', function() {
            window.location.href = `/delete_program/${programId}`;
        });
    });
});