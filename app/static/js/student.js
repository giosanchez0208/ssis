$(document).ready(function() {
    $('#student_table').DataTable({
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
});


// Show the custom gender field if "Custom" is selected
const customRadio = document.getElementById('custom');
const customGenderField = document.getElementById('customGenderField');

customRadio.addEventListener('change', function () {
    if (this.checked) {
        customGenderField.style.display = 'block';
    }
});

document.querySelectorAll('input[name="gender"]').forEach(radio => {
    radio.addEventListener('change', function () {
        if (this.id !== 'custom') {
            customGenderField.style.display = 'none';
        }
    });
});

// Apply the input mask and handle ID check
$(document).ready(function () {
    $('#idNumber').inputmask("9999-9999", {
        placeholder: "####-####",
        showMaskOnHover: false,
        onIncomplete: function () {
            $(this).val("");
        }
    });

    document.getElementById('idNumber').addEventListener('blur', function () {
        var fullId = this.value;

        fetch('/check_id', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    id_num: fullId
                }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.exists) {
                    document.getElementById('idError').style.display = 'block';
                } else {
                    document.getElementById('idError').style.display = 'none';
                }
            });
    });
});

// Validate form and enable/disable submit button
document.addEventListener('DOMContentLoaded', function () {
    const submitBtn = document.getElementById('submitBtn');
    const idInput = document.getElementById('idNumber');
    const firstNameInput = document.getElementById('firstName');
    const lastNameInput = document.getElementById('lastName');
    const yearInput = document.getElementById('year');
    const genderInputs = document.querySelectorAll('input[name="gender"]');
    let isValidId = false; // Tracks if ID is valid

    // Helper function to check if all required fields are filled
    function checkFormValidity() {
        const isFirstNameFilled = firstNameInput.value.trim() !== '';
        const isLastNameFilled = lastNameInput.value.trim() !== '';
        const isYearSelected = yearInput.value !== '';
        const isGenderSelected = Array.from(genderInputs).some(input => input.checked);

        // Enable the button if all conditions are met
        submitBtn.disabled = !(isValidId && isFirstNameFilled && isLastNameFilled && isYearSelected && isGenderSelected);
    }

    // ID validation (checking format and if it's unique)
    idInput.addEventListener('blur', function () {
        const fullId = this.value;
        fetch('/check_id', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    id_num: fullId
                }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.exists) {
                    document.getElementById('idError').style.display = 'block';
                    isValidId = false;
                } else {
                    document.getElementById('idError').style.display = 'none';
                    isValidId = true;
                }
                checkFormValidity(); // Recheck form after ID validation
            });
    });

    // Add input listeners to recheck form on changes
    firstNameInput.addEventListener('input', checkFormValidity);
    lastNameInput.addEventListener('input', checkFormValidity);
    yearInput.addEventListener('change', checkFormValidity);
    genderInputs.forEach(input => input.addEventListener('change', checkFormValidity));

    // Initial check in case of any pre-filled values
    checkFormValidity();
});

// Handle edit modal logic
document.addEventListener('DOMContentLoaded', function () {
    const editModal = document.getElementById('editModal');

    editModal.addEventListener('show.bs.modal', function (event) {
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
    editForm.addEventListener('submit', function (e) {
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