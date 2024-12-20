async function initializeStudentTable() {
    return new Promise((resolve, reject) => {
        try {
            // Initialize the DataTable
            var table = $('#student_table').DataTable({
                processing: true,
                serverSide: true,
                ajax: {
                    url: '/students/data',
                    type: 'POST',
                    data: function(d) {
                        d.courseFilter = $('#courseFilter').val();
                    }
                },
                columns: [
                    { 
                        data: null,
                        orderable: false,
                        searchable: false,
                        render: function (data, type, row) {
                            if (row.profile_picture_id) {
                                const cloudinaryUrl = `https://res.cloudinary.com/${cloudinaryCloudName}/image/upload/c_fill,h_30,w_30/${row.profile_picture_id}`;
                                return `<img src="${cloudinaryUrl}" alt="Profile Picture" class="rounded-circle mx-2" width="30" height="30" style="object-fit: cover;">`;
                            } else {
                                return `<img src="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgdmlld0JveD0iMCAwIDEwMCAxMDAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CiAgPHJlY3Qgd2lkdGg9IjEwMCIgaGVpZ2h0PSIxMDAiIGZpbGw9IiNmMGYwZjAiLz4KICA8Y2lyY2xlIGN4PSI1MCIgY3k9IjM1IiByPSIxOCIgZmlsbD0iIzg4ODg4OCIvPgogIDxwYXRoIGQ9Ik0yNSA4NUMyNSA2OCAzNiA1NSA1MCA1NVM3NSA2OCA3NSA4NVYxMDBIMjVWODVaIiBmaWxsPSIjODg4ODg4Ii8+Cjwvc3ZnPgo=" alt="Default Profile Picture" class="rounded-circle mx-2" width="30" height="30" style="object-fit: cover;">`;
                            }
                        }
                    },
                    { data: 'id_num', orderable: true },
                    { 
                        data: null,
                        orderable: true,
                        render: function (data, type, row) {
                            return `<b>${data.last_name}</b>, ${data.first_name}`;
                        }
                    },
                    { data: 'year_level', orderable: true, className: 'hide-on-mobile-view' },
                    { 
                        data: 'course',
                        orderable: true,
                        render: function(data, type, row) {
                            if (!data || data === 'none' || data === '') {
                                return '<span class="text-secondary">Not Enrolled</span>';
                            }
                            return data;
                        }
                    },
                    { data: 'gender', orderable: true, className: 'hide-on-mobile-view' },
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

            // Listen for the `init` event and resolve the Promise
            table.on('init', function() {
                resolve(table);
            });
        } catch (error) {
            reject(error);
        }
    });
}

$(document).ready(function() {
    // Initialize the DataTable
    var table = $('#student_table').DataTable({
        processing: true,
        serverSide: true,
        ajax: {
            url: '/students/data',
            type: 'POST',
            data: function(d) {
                d.courseFilter = $('#courseFilter').val();
            }
        },
        columns: [
            { 
                data: null,
                orderable: false,
                searchable: false,
                render: function (data, type, row) {
                    if (row.profile_picture_id) {
                        const cloudinaryUrl = `https://res.cloudinary.com/${cloudinaryCloudName}/image/upload/c_fill,h_30,w_30/${row.profile_picture_id}`;
                        return `<img src="${cloudinaryUrl}" alt="Profile Picture" class="rounded-circle mx-2" width="30" height="30" style="object-fit: cover;">`;
                    } else {
                        // Return default profile picture if no profile_picture_id exists
                        return `<img src="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgdmlld0JveD0iMCAwIDEwMCAxMDAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CiAgPHJlY3Qgd2lkdGg9IjEwMCIgaGVpZ2h0PSIxMDAiIGZpbGw9IiNmMGYwZjAiLz4KICA8Y2lyY2xlIGN4PSI1MCIgY3k9IjM1IiByPSIxOCIgZmlsbD0iIzg4ODg4OCIvPgogIDxwYXRoIGQ9Ik0yNSA4NUMyNSA2OCAzNiA1NSA1MCA1NVM3NSA2OCA3NSA4NVYxMDBIMjVWODVaIiBmaWxsPSIjODg4ODg4Ii8+Cjwvc3ZnPgo=" alt="Default Profile Picture" class="rounded-circle mx-2" width="30" height="30" style="object-fit: cover;">`;
                    }
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
                orderable: true,
                render: function(data, type, row) {
                    if (!data || data === 'none' || data === '') {
                        return '<span class="text-secondary">Not Enrolled</span>';
                    }
                    return data;
                }
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

    // if /edit then load modal
    table.on('init', function() {
        const urlParams = new URLSearchParams(window.location.search);
        const studentId = urlParams.get('id');
        if (studentId) {
            fetch(`/students/edit/${studentId}`)
            .then(response => response.json())
            .then(student => {
                const modal = new bootstrap.Modal(document.getElementById('editModal'));
                
                // Populate form fields
                document.getElementById('editIdNumber').value = student.id_num;
                document.getElementById('editFirstName').value = student.first_name;
                document.getElementById('editLastName').value = student.last_name;
                document.getElementById('editCourse').value = student.course || '';
                document.getElementById('editYear').value = student.year_level;
                
                // Handle profile picture
                const profilePreview = document.getElementById('editProfilePreview');
                if (student.profile_picture_id) {
                    profilePreview.src = `https://res.cloudinary.com/${cloudinaryCloudName}/image/upload/c_fill,h_100,w_100/${student.profile_picture_id}`;
                }
                
                // Handle gender selection
                const genderRadios = document.getElementsByName('gender');
                let foundMatchingGender = false;

                genderRadios.forEach(radio => {
                    if (radio.value === student.gender) {
                        radio.checked = true;
                        foundMatchingGender = true;
                    }
                });

                const customRadio = document.getElementById('editCustom');
                const customGenderField = document.getElementById('editCustomGenderField');
                const customGenderInput = document.getElementById('editCustomGender');

                if (!foundMatchingGender) {
                    customRadio.checked = true;
                    customGenderField.style.display = 'block';
                    customGenderInput.value = student.gender;
                } else {
                    customGenderField.style.display = 'none';
                    customGenderInput.value = '';
                }
                
                // Show modal
                modal.show();
            })
            .catch(error => {
                console.error('Error fetching student data:', error);
                alert('Failed to load student data');
            });
        }
    });

    // Course filter change handler
    $('#courseFilter').on('change', function() {
        table.ajax.reload();
    });

    // Cloudinary upload function
    async function uploadToCloudinary(file, studentId = null) {
        console.log('Starting uploadToCloudinary', { 
            fileName: file.name, 
            fileSize: file.size, 
            fileType: file.type,
            studentId 
        });
        
        const formData = new FormData();
        formData.append('image', file);
        if (studentId) {
            formData.append('student_id', studentId);
        }
        
        try {
            const endpoint = studentId ? '/cloudinary/update' : '/cloudinary/upload';
            console.log('Uploading to endpoint:', endpoint);
            
            const response = await fetch(endpoint, {
                method: 'POST',
                body: formData
            });
            
            console.log('Upload response status:', response.status);
            const responseText = await response.text();
            console.log('Raw response:', responseText);
            
            let data;
            try {
                data = JSON.parse(responseText);
            } catch (e) {
                console.error('Failed to parse response as JSON:', e);
                throw new Error('Invalid response from server');
            }
            
            console.log('Parsed response data:', data);
            
            if (!response.ok) {
                throw new Error(data.error || 'Upload failed');
            }
            
            return data.public_id;
        } catch (error) {
            console.error('Upload error:', error);
            throw error;
        }
    }
    
    // fetch and populate programs dropdown
    fetch('/students/get_programs')
        .then(response => response.json())
        .then(programs => {
            programs.sort((a, b) => a.course_name.localeCompare(b.course_name));
            const courseDropdown = document.getElementById("course");
            courseDropdown.innerHTML = "";

            // add the "Not enrolled in any program" option first
            const defaultOption = document.createElement("option");
            defaultOption.value = "none";
            defaultOption.textContent = "Not enrolled in any program";
            courseDropdown.appendChild(defaultOption);

            // add all other programs
            programs.forEach(program => {
                const option = document.createElement("option");
                option.value = program.course_code;
                option.textContent = `${program.course_code} - ${program.course_name}`;
                courseDropdown.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Error fetching programs:', error);
        });

    // delete modal logic
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

    // custom gender field logic
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

    // ID number input mask
    $('#idNumber').inputmask("9999-9999", {
        placeholder: "YYYY-NNNN",
        showMaskOnHover: false,
        onIncomplete: function () {
            $(this).val("");
            $('#submitBtn').prop('disabled', true);
        }
    });

    // form validation logic
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

            submitBtn.disabled = !(isValidId && isFirstNameFilled && isLastNameFilled && isYearSelected && isGenderSelected);
        }

        idInput.addEventListener('blur', function () {
            const fullId = this.value;
            fetch('/students/check_id', {
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

        firstNameInput.addEventListener('input', checkFormValidity);
        lastNameInput.addEventListener('input', checkFormValidity);
        yearInput.addEventListener('change', checkFormValidity);
        genderInputs.forEach(input => input.addEventListener('change', checkFormValidity));

        idInput.addEventListener('input', function () {
            const value = idInput.value;
            const isFormatValid = /^\d{4}-\d{4}$/.test(value);
            isValidId = isFormatValid;
            checkFormValidity();
        });

        checkFormValidity();
    }

    validateForm();

    // Edit modal logic
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
    
                // Reset the file input
                document.getElementById('editProfilePicture').value = '';

                // Set the profile picture preview
                const profilePreview = document.getElementById('editProfilePreview');
                if (student.profile_picture_id) {
                    const cloudinaryUrl = `https://res.cloudinary.com/${cloudinaryCloudName}/image/upload/c_fill,h_100,w_100/${student.profile_picture_id}`;
                    profilePreview.src = cloudinaryUrl;
                } else {
                    profilePreview.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgdmlld0JveD0iMCAwIDEwMCAxMDAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CiAgPHJlY3Qgd2lkdGg9IjEwMCIgaGVpZ2h0PSIxMDAiIGZpbGw9IiNmMGYwZjAiLz4KICA8Y2lyY2xlIGN4PSI1MCIgY3k9IjM1IiByPSIxOCIgZmlsbD0iIzg4ODg4OCIvPgogIDxwYXRoIGQ9Ik0yNSA4NUMyNSA2OCAzNiA1NSA1MCA1NVM3NSA2OCA3NSA4NVYxMDBIMjVWODVaIiBmaWxsPSIjODg4ODg4Ii8+Cjwvc3ZnPgo=';
                }
    
                // Toggle the remove button based on profile picture presence
                toggleRemoveButton();

                // Handle gender selection
                const genderRadios = document.getElementsByName('gender');
                let foundMatchingGender = false;

                // First try to match with standard options (Male/Female)
                genderRadios.forEach(radio => {
                    if (radio.value === student.gender) { 
                        radio.checked = true;
                        foundMatchingGender = true;
                    } else {
                        radio.checked = false;
                    }
                });

                // If no standard gender matches, it must be a custom gender
                const customRadio = document.getElementById('editCustom');
                const customGenderField = document.getElementById('editCustomGenderField');
                const customGenderInput = document.getElementById('editCustomGender');

                if (!foundMatchingGender) {
                    customRadio.checked = true;
                    customGenderField.style.display = 'block';
                    customGenderInput.value = student.gender;
                } else {
                    customGenderField.style.display = 'none';
                    customGenderInput.value = '';
                }

                if (!foundMatchingGender) {
                    customRadio.checked = true;
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

    // Edit form submit handler
    const editForm = document.getElementById('editForm');
    editForm.addEventListener('submit', async function (e) {
        e.preventDefault();
        console.log('Edit form submit started');
        
        const submitBtn = this.querySelector('button[type="submit"]');
        submitBtn.disabled = true;
        
        try {
            const formData = new FormData(this);
            const fileInput = document.getElementById('editProfilePicture');
            const file = fileInput.files[0];
            const studentId = document.getElementById('editIdNumber').value;
            
            console.log('Form data:', {
                hasFile: !!file,
                studentId,
                formFields: Array.from(formData.entries())
            });
            
            if (file) {
                console.log('Uploading file to Cloudinary...', {
                    fileName: file.name,
                    fileSize: file.size,
                    fileType: file.type
                });
                const imageUrl = await uploadToCloudinary(file, studentId);
                console.log('Got image URL:', imageUrl);
                formData.set('profile_picture_id', imageUrl);
            }
            
            console.log('Submitting to edit endpoint...');
            const response = await fetch(`/students/edit/${studentId}`, {
                method: 'POST',
                body: formData
            });

            const responseData = await response.json();
            console.log('Edit response:', responseData);

            if (responseData.success) {
                alert('Student updated successfully');
                $('#student_table').DataTable().ajax.reload();
            } else {
                throw new Error(responseData.message || 'Failed to update student');
            }
        } catch (error) {
            console.error('Update failed:', error);
            alert('Failed to update student: ' + error.message);
        } finally {
            submitBtn.disabled = false;
        }
    });

    // show/hide remove button based on profile picture presence
    const editProfilePictureInput = document.getElementById('editProfilePicture');
    const deleteProfilePictureButton = document.getElementById('deleteProfilePicture');
    const editProfilePreview = document.getElementById('editProfilePreview');

    function toggleRemoveButton() {
        if (editProfilePreview.src.includes('data:image/svg+xml') || editProfilePictureInput.files.length > 0) {
            deleteProfilePictureButton.style.display = 'none';
        } else {
            deleteProfilePictureButton.style.display = 'inline-block';
        }
    }

    deleteProfilePictureButton.addEventListener('click', async function (e) {
        e.preventDefault();
        const studentId = document.getElementById('editIdNumber').value;
        const confirmDelete = confirm('Are you sure you want to remove the profile picture?');
        if (!confirmDelete) {
            return;
        }
        try {
            const response = await fetch(`/cloudinary/delete/${studentId}`, {
                method: 'POST'
            });
            const responseData = await response.json();
            if (responseData.success) {
                editProfilePreview.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgdmlld0JveD0iMCAwIDEwMCAxMDAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CiAgPHJlY3Qgd2lkdGg9IjEwMCIgaGVpZ2h0PSIxMDAiIGZpbGw9IiNmMGYwZjAiLz4KICA8Y2lyY2xlIGN4PSI1MCIgY3k9IjM1IiByPSIxOCIgZmlsbD0iIzg4ODg4OCIvPgogIDxwYXRoIGQ9Ik0yNSA4NUMyNSA2OCAzNiA1NSA1MCA1NVM3NSA2OCA3NSA4NVYxMDBIMjVWODVaIiBmaWxsPSIjODg4ODg4Ii8+Cjwvc3ZnPgo=';
                toggleRemoveButton();
                $('#student_table').DataTable().ajax.reload();
            } else {
                throw new Error(responseData.message || 'Failed to delete profile picture');
            }
        } catch (error) {
            console.error('Delete failed:', error);
            alert('Failed to delete profile picture: ' + error.message);
        }
    });

    editProfilePictureInput.addEventListener('change', function () {
        const file = this.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function (e) {
                editProfilePreview.src = e.target.result;
                toggleRemoveButton();
            };
            reader.readAsDataURL(file);
        }
    });

    deleteProfilePictureButton.addEventListener('click', async function (e) {
        e.preventDefault();
        const studentId = document.getElementById('editIdNumber').value;
        try {
            const response = await fetch(`/cloudinary/delete/${studentId}`, {
                method: 'POST'
            });
            const responseData = await response.json();
            if (responseData.success) {
                editProfilePreview.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgdmlld0JveD0iMCAwIDEwMCAxMDAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CiAgPHJlY3Qgd2lkdGg9IjEwMCIgaGVpZ2h0PSIxMDAiIGZpbGw9IiNmMGYwZjAiLz4KICA8Y2lyY2xlIGN4PSI1MCIgY3k9IjM1IiByPSIxOCIgZmlsbD0iIzg4ODg4OCIvPgogIDxwYXRoIGQ9Ik0yNSA4NUMyNSA2OCAzNiA1NSA1MCA1NVM3NSA2OCA3NSA4NVYxMDBIMjVWODVaIiBmaWxsPSIjODg4ODg4Ii8+Cjwvc3ZnPgo=';
                toggleRemoveButton();
                $('#student_table').DataTable().ajax.reload();
            } else {
                throw new Error(responseData.message || 'Failed to delete profile picture');
            }
        } catch (error) {
            console.error('Delete failed:', error);
            alert('Failed to delete profile picture: ' + error.message);
        }
    });

    editProfilePictureInput.addEventListener('change', function () {
        const file = this.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function (e) {
                editProfilePreview.src = e.target.result;
                toggleRemoveButton();
            };
            reader.readAsDataURL(file);
        }
    });

    // Create form submit handler
    const createForm = document.querySelector('#createModal form');
    if (createForm) {
        createForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const submitBtn = this.querySelector('button[type="submit"]');
            submitBtn.disabled = true;
            
            try {
                const formData = new FormData(this);
                const fileInput = document.getElementById('profilePicture');
                const file = fileInput.files[0];
                
                if (file) {
                    console.log('Uploading file to Cloudinary...');
                    const imageUrl = await uploadToCloudinary(file);
                    formData.set('profile_picture_id', imageUrl);
                }

                const response = await fetch(this.action, {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) {
                    throw new Error('Failed to create student');
                }

                window.location.reload();
                $('#student_table').DataTable().ajax.reload();
            } catch (error) {
                console.error('Submission failed:', error);
                alert('Failed to create student: ' + error.message);
            } finally {
                submitBtn.disabled = false;
            }
        });
    }

    // Image preview functionality
    function initializeImagePreview(inputId, previewId) {
        const input = document.getElementById(inputId);
        const preview = document.getElementById(previewId);
        
        if (!input || !preview) return;
        
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (!file) return;
            
            if (file.size > 2 * 1024 * 1024) {
                alert('File size must be less than 2MB');
                input.value = '';
                return;
            }
            
            if (!file.type.startsWith('image/')) {
                alert('Please select an image file');
                input.value = '';
                return;
            }
            
            const reader = new FileReader();
            reader.onload = function(event) {
                preview.src = event.target.result;
            };
            reader.readAsDataURL(file);
        });
    }

    // Initialize image previews
    initializeImagePreview('profilePicture', 'profilePreview');
    initializeImagePreview('editProfilePicture', 'editProfilePreview');

    // Edit modal gender field logic
    const editCustomRadio = document.getElementById('editCustom');
    const editCustomGenderField = document.getElementById('editCustomGenderField');

    editCustomRadio.addEventListener('change', function () {
        editCustomGenderField.style.display = this.checked ? 'block' : 'none';
    });

    // Test Cloudinary configuration
    async function testCloudinaryConfig() {
        try {
            const response = await fetch('/cloudinary/test_config');
            const data = await response.json();
            console.log('Cloudinary config test:', data);
        } catch (error) {
            console.error('Failed to test Cloudinary config:', error);
        }
    }
    testCloudinaryConfig();

    document.querySelectorAll('#editModal input[name="gender"]').forEach(radio => {
        radio.addEventListener('change', function() {
            const customField = document.getElementById('editCustomGenderField');
            if (this.id === 'editCustom') {
                customField.style.display = 'block';
            } else {
                customField.style.display = 'none';
                document.getElementById('editCustomGender').value = '';
            }
        });
    });
});