function downloadFile(fileData) {
		const blob = new Blob([fileData], { type: 'application/octet-stream' });
		const link = document.createElement('a');
		link.href = URL.createObjectURL(blob);
		link.download = fileName;
		document.body.appendChild(link);
		link.click();
		document.body.removeChild(link);
	}