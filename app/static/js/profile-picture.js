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

async function handleEditFormSubmit(e) {
    e.preventDefault();
    console.log('Edit form submit started');
    
    const submitBtn = e.target.querySelector('button[type="submit"]');
    submitBtn.disabled = true;
    
    try {
        const formData = new FormData(e.target);
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
        } else {
            console.log('No file selected for upload');
        }
        
        console.log('Submitting to edit endpoint...');
        const response = await fetch(`/students/edit/${studentId}`, {
            method: 'POST',
            body: formData
        });

        const responseData = await response.json();
        console.log('Edit response:', responseData);

        if (!response.ok) {
            throw new Error(responseData.message || 'Failed to update student');
        }

        window.location.reload();
    } catch (error) {
        console.error('Update failed:', error);
        alert('Failed to update student: ' + error.message);
    } finally {
        submitBtn.disabled = false;
    }
}

// Test Cloudinary configuration on page load
document.addEventListener('DOMContentLoaded', async function() {
    try {
        const response = await fetch('/cloudinary/test_config');
        const data = await response.json();
        console.log('Cloudinary config test:', data);
    } catch (error) {
        console.error('Failed to test Cloudinary config:', error);
    }
});