$(document).ready(function() {
    // Initialize DataTable
    $('#student_table').DataTable({
        columnDefs: [
            { orderable: false, targets: [-2] },
            { orderable: false, targets: [-1] }
        ],
        initComplete: function(settings, json) {
            $('.dataTables_filter input[name="search"]')
                .attr('placeholder', 'Search...');
        }
    });

    // Delete Modal Logic
    $('#deleteModal').on('show.bs.modal', function(event) {
        const button = $(event.relatedTarget);
        const studentName = button.data('student-name');
        const studentId = button.data('id');
        const modal = $(this);
        
        modal.find('#studentName').text(studentName);
        modal.find('#studentId').text(studentId);
        
        modal.find('#confirmDeleteBtn').off('click').on('click', function() {
            window.location.href = `/delete/${studentId}`;
        });
    });

    // Custom Gender Field Logic
    const customRadio = document.getElementById('custom');
    const customGenderField = document.getElementById('customGenderField');

    customRadio.addEventListener('change', function() {
        customGenderField.style.display = this.checked ? 'block' : 'none';
    });

    document.querySelectorAll('input[name="gender"]').forEach(radio => {
        radio.addEventListener('change', function() {
            if (this.id !== 'custom') {
                customGenderField.style.display = 'none';
            }
        });
    });

    // ID Number Input Mask and Validation
    $('#idNumber').inputmask("9999-9999", {
        placeholder: "YYYY-NNNN",
        showMaskOnHover: false,
        onIncomplete: function() {
            $(this).val("");
            enableSubmitButton(false);
        }
    });

    const idInput = $('#idNumber');
    const submitBtn = $('#submitBtn');
    let isValidId = false;

    idInput.on('input blur', function() {
        validateIdNumber(this.value);
    });

    idInput.on('blur', function() {
        const fullId = this.value;
        fetch('/check_id', {
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
            enableSubmitButton(isValidId);
        });
    });

    function validateIdNumber(id) {
        const regex = /^\d{4}-\d{4}$/;
        enableSubmitButton(regex.test(id) && isValidId);
    }

    // Validate Form
    const firstNameInput = document.getElementById('firstName');
    const lastNameInput = document.getElementById('lastName');
    const yearInput = document.getElementById('year');
    const genderInputs = document.querySelectorAll('input[name="gender"]');

    function enableSubmitButton(enable) {
        submitBtn.prop('disabled', !enable);
    }

    function checkFormValidity() {
        const isFirstNameFilled = firstNameInput.value.trim() !== '';
        const isLastNameFilled = lastNameInput.value.trim() !== '';
        const isYearSelected = yearInput.value !== '';
        const isGenderSelected = Array.from(genderInputs).some(input => input.checked);
        
        enableSubmitButton(isValidId && isFirstNameFilled && isLastNameFilled && isYearSelected && isGenderSelected);
    }

    // Add input listeners
    [firstNameInput, lastNameInput, yearInput].forEach(input => {
        input.addEventListener('input', checkFormValidity);
    });
    genderInputs.forEach(input => input.addEventListener('change', checkFormValidity));

    // Initial check in case of any pre-filled values
    checkFormValidity();

    // Edit Modal Logic
    const editModal = document.getElementById('editModal');

    editModal.addEventListener('show.bs.modal', function(event) {
        const button = event.relatedTarget;
        const studentId = button.getAttribute('data-id');

        fetch(`/edit/${studentId}`)
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
    editForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(this);
        const studentId = document.getElementById('editIdNumber').value;

        fetch(`/edit/${studentId}`, {
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
        radio.addEventListener('change', function() {
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
