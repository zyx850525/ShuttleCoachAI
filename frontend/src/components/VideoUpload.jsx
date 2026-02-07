import React, { useState, useRef, useEffect } from 'react';
import { useLanguage } from '../LanguageContext';

const VideoUpload = ({ onUploadSuccess }) => {
  const { t } = useLanguage();
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState('');

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      setFile(selectedFile);
      setError('');
      setProgress(0);
      
      const url = URL.createObjectURL(selectedFile);
      setPreviewUrl(url);
    }
  };

  useEffect(() => {
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
    };
  }, [previewUrl]);

  const handleUpload = () => {
    if (!file) {
      setError('请选择视频文件');
      return;
    }

    setUploading(true);
    setProgress(0);
    const formData = new FormData();
    formData.append('file', file);

    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/api/upload');

    xhr.upload.onprogress = (event) => {
      if (event.lengthComputable) {
        const percentComplete = (event.loaded / event.total) * 100;
        setProgress(Math.round(percentComplete));
      }
    };

    xhr.onload = () => {
      if (xhr.status === 200) {
        try {
          const data = JSON.parse(xhr.responseText);
          onUploadSuccess(data.task_id);
        } catch (e) {
          setError('解析响应失败');
        }
      } else {
        setError('上传失败，请重试');
      }
      setUploading(false);
    };

    xhr.onerror = () => {
      setError('网络错误');
      setUploading(false);
    };

    xhr.send(formData);
  };

  return (
    <div style={styles.container}>
      <h2>🏸 {t('upload_title')}</h2>
      <p style={styles.hint}>{t('upload_hint')}</p>
      
      <div style={styles.uploadBox}>
        <label style={styles.fileLabel}>
          {t('upload_choose_file')}
          <input 
            type="file" 
            accept="video/*" 
            onChange={handleFileChange}
            style={styles.hiddenInput}
          />
        </label>
        
        {previewUrl && (
          <div style={styles.previewContainer}>
            <video src={previewUrl} controls style={styles.videoPreview} />
            <p style={styles.fileName}>{file.name}</p>
          </div>
        )}
        
        {uploading && (
          <div style={styles.progressBarContainer}>
            <div style={{...styles.progressBarFill, width: `${progress}%`}}></div>
            <span style={styles.progressText}>{progress}%</span>
          </div>
        )}

        <button 
          onClick={handleUpload} 
          disabled={!file || uploading}
          style={styles.button}
        >
          {uploading ? t('upload_button_processing') : t('upload_button_start')}
        </button>
      </div>
      
      {error && <p style={styles.error}>{error}</p>}
    </div>
  );
};

const styles = {
  container: {
    textAlign: 'center',
    padding: '40px',
    backgroundColor: '#f9f9f9',
    borderRadius: '12px',
    maxWidth: '600px',
    margin: '0 auto',
    boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
  },
  hint: {
    color: '#666',
    marginBottom: '20px'
  },
  uploadBox: {
    display: 'flex',
    flexDirection: 'column',
    gap: '20px',
    alignItems: 'center'
  },
  fileLabel: {
    padding: '10px 20px',
    backgroundColor: '#eee',
    borderRadius: '4px',
    cursor: 'pointer',
    border: '1px solid #ccc',
    fontWeight: '500',
    display: 'inline-block'
  },
  hiddenInput: {
    display: 'none'
  },
  previewContainer: {
    width: '100%',
    maxWidth: '400px',
    borderRadius: '8px',
    overflow: 'hidden',
    backgroundColor: '#000',
  },
  videoPreview: {
    width: '100%',
    height: 'auto',
    display: 'block'
  },
  fileName: {
    color: '#fff',
    backgroundColor: '#333',
    padding: '8px',
    margin: 0,
    fontSize: '0.9em'
  },
  progressBarContainer: {
    width: '100%',
    maxWidth: '400px',
    height: '20px',
    backgroundColor: '#e0e0e0',
    borderRadius: '10px',
    overflow: 'hidden',
    position: 'relative',
    marginTop: '10px'
  },
  progressBarFill: {
    height: '100%',
    backgroundColor: '#4caf50',
    transition: 'width 0.2s ease-in-out'
  },
  progressText: {
    position: 'absolute',
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    color: '#333',
    fontSize: '12px',
    fontWeight: 'bold'
  },
  button: {
    padding: '12px 36px',
    fontSize: '16px',
    backgroundColor: '#1a73e8',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    opacity: (props) => props.disabled ? 0.6 : 1,
    marginTop: '10px'
  },
  error: {
    color: 'red',
    marginTop: '10px'
  }
};

export default VideoUpload;
