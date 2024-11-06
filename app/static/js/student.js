$(document).ready(function() {
    
    // Initialize the DataTable
    var table = $('#student_table').DataTable({
        processing: true,
        serverSide: true,
        ajax: {
            url: '/students/data',
            type: 'POST',
            data: function(d) {
                // Add the course filter value to the data sent to the server
                d.courseFilter = $('#courseFilter').val();
            }
        },
        columns: [
            { 
                data: null,
                orderable: false,
                searchable: false,
                render: function (data, type, row) {
                    return `<img src="" alt="Profile Picture" class="rounded-circle mx-2" width="30" height="30">`;
                }
            },
            { 
                data: 'id_num',
                orderable: true
            },
            { 
                data: null,
                orderable: true,
                render: function (data, type, row) {
                    return `<b>${data.last_name}</b>, ${data.first_name}`;
                }
            },
            { 
                data: 'year_level',
                orderable: true,
                className: 'hide-on-mobile-view'
            },
            { 
                data: 'course',
                orderable: true
            },
            { 
                data: 'gender',
                orderable: true,
                className: 'hide-on-mobile-view'
            },
            {
                data: null,
                orderable: false,
                searchable: false,
                className: 'button-column',
                render: function (data, type, row) {
                    return `
                        <button class="btn btn-warning btn-sm edit-btn" data-bs-toggle="modal"
                            data-bs-target="#editModal" data-id="${row.id_num}">
                            <i class="fas fa-edit p-1"></i>
                        </button>
                    `;
                }
            },
            {
                data: null,
                orderable: false,
                searchable: false,
                className: 'button-column',
                render: function (data, type, row) {
                    return `
                        <button class="btn btn-danger btn-sm" data-bs-toggle="modal" data-bs-target="#deleteModal"
                            data-student-name="${row.last_name}, ${row.first_name}"
                            data-id="${row.id_num}">
                            <i class="fas fa-trash p-1"></i>
                        </button>
                    `;
                }
            }
        ],
        pageLength: 10,
        lengthMenu: [10, 25, 50, 100]
    });

    $('#courseFilter').on('change', function() {
        table.ajax.reload();
    });


    // Fetch programs and populate dropdown
    fetch(`/students/get_programs`)  // Adjust this URL to your actual endpoint
        .then(response => response.json())
        .then(programs => {
            programs.sort((a, b) => a.course_name.localeCompare(b.course_name));
            const courseDropdown = document.getElementById("course");
            courseDropdown.innerHTML = ""; // Clear existing options

            programs.forEach(program => {
                const option = document.createElement("option");
                option.value = program.course_code;
                option.textContent = `${program.course_code} - ${program.course_name}`; // Format changed
                courseDropdown.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Error fetching programs:', error);
        });

    // Delete modal logic
    $('#deleteModal').on('show.bs.modal', function(event) {
        var button = $(event.relatedTarget);
        var studentName = button.data('student-name');
        var studentId = button.data('id');
        
        var modal = $(this);
        modal.find('#studentName').text(studentName);
        modal.find('#studentId').text(studentId);
        
        modal.find('#confirmDeleteBtn').off('click').on('click', function() {
            window.location.href = `/students/delete/${studentId}`;
        });
    });

    // Show/hide custom gender field
    const customRadio = document.getElementById('custom');
    const customGenderField = document.getElementById('customGenderField');

    customRadio.addEventListener('change', function () {
        customGenderField.style.display = this.checked ? 'block' : 'none';
    });

    document.querySelectorAll('input[name="gender"]').forEach(radio => {
        radio.addEventListener('change', function () {
            if (this.id !== 'custom') {
                customGenderField.style.display = 'none';
            }
        });
    });

    // Input mask for ID number
    $('#idNumber').inputmask("9999-9999", {
        placeholder: "YYYY-NNNN",
        showMaskOnHover: false,
        onIncomplete: function () {
            $(this).val("");
            $('#submitBtn').prop('disabled', true);
        }
    });

    // Validate ID number and control submit button state
    validateForm();

    function validateForm() {
        const submitBtn = document.getElementById('submitBtn');
        const idInput = document.getElementById('idNumber');
        const firstNameInput = document.getElementById('firstName');
        const lastNameInput = document.getElementById('lastName');
        const yearInput = document.getElementById('year');
        const genderInputs = document.querySelectorAll('input[name="gender"]');
        let isValidId = false;

        function checkFormValidity() {
            const isFirstNameFilled = firstNameInput.value.trim() !== '';
            const isLastNameFilled = lastNameInput.value.trim() !== '';
            const isYearSelected = yearInput.value !== '';
            const isGenderSelected = Array.from(genderInputs).some(input => input.checked);

            // Enable the button if all conditions are met
            submitBtn.disabled = !(isValidId && isFirstNameFilled && isLastNameFilled && isYearSelected && isGenderSelected);
        }

        // ID validation on blur
        idInput.addEventListener('blur', function () {
            const fullId = this.value;
            fetch(`/students/check_id`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ id_num: fullId }),
            })
            .then(response => response.json())
            .then(data => {
                isValidId = !data.exists;
                document.getElementById('idError').style.display = data.exists ? 'block' : 'none';
                checkFormValidity();
            });
        });

        // Add input listeners to recheck form on changes
        firstNameInput.addEventListener('input', checkFormValidity);
        lastNameInput.addEventListener('input', checkFormValidity);
        yearInput.addEventListener('change', checkFormValidity);
        genderInputs.forEach(input => input.addEventListener('change', checkFormValidity));

        // ID number format validation on input
        idInput.addEventListener('input', function () {
            const value = idInput.value;
            const isFormatValid = /^\d{4}-\d{4}$/.test(value);
            isValidId = isFormatValid;
            checkFormValidity();
        });

        // Initial check in case of any pre-filled values
        checkFormValidity();
    }

    // Handle edit modal logic
    const editModal = document.getElementById('editModal');

    editModal.addEventListener('show.bs.modal', function (event) {
        const button = event.relatedTarget;
        const studentId = button.getAttribute('data-id');

        fetch(`/students/edit/${studentId}`)
            .then(response => response.json())
            .then(student => {
                document.getElementById('editIdNumber').value = student.id_num;
                document.getElementById('editFirstName').value = student.first_name;
                document.getElementById('editLastName').value = student.last_name;
                document.getElementById('editCourse').value = student.course || '';
                document.getElementById('editYear').value = student.year_level;

                const genderRadios = document.querySelectorAll('input[name="gender"]');
                genderRadios.forEach(radio => {
                    radio.checked = radio.value === student.gender;
                });

                const customGenderField = document.getElementById('editCustomGenderField');
                const customGenderInput = document.getElementById('editCustomGender');
                if (student.gender !== 'Male' && student.gender !== 'Female') {
                    document.getElementById('editCustom').checked = true;
                    customGenderField.style.display = 'block';
                    customGenderInput.value = student.gender;
                } else {
                    customGenderField.style.display = 'none';
                    customGenderInput.value = '';
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while fetching student data.');
            });
    });

    const editForm = document.getElementById('editForm');
    editForm.addEventListener('submit', function (e) {
        e.preventDefault();
        const formData = new FormData(this);
        const studentId = document.getElementById('editIdNumber').value;

        fetch(`/students/edit/${studentId}`, {
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
                alert(data.message || 'An error occurred while updating the student.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while updating the student.');
        });
    });

    // Show/hide custom gender field in edit form
    document.querySelectorAll('input[name="gender"]').forEach(radio => {
        radio.addEventListener('change', function () {
            const customGenderField = document.getElementById('editCustomGenderField');
            const customGenderInput = document.getElementById('editCustomGender');
            if (this.id === 'editCustom') {
                customGenderField.style.display = 'block';
                customGenderInput.required = true;
            } else {
                customGenderField.style.display = 'none';
                customGenderInput.required = false;
                customGenderInput.value = '';
            }
        });
    });
});
