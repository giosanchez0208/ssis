$(document).ready(function () {
    const collegeTable = initializeDataTable();
    setupCreateCollegeForm();
    setupCollegeCodeValidation();
    setupEditCollege();
    setupDeleteCollege();
});

function initializeDataTable() {
    return $('#college_table').DataTable({
        columnDefs: [
            { orderable: false, targets: [-2, -1] }
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
