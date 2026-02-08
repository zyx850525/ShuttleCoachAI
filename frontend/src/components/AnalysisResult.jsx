import React, { useState } from 'react';
import { useLanguage } from '../LanguageContext';
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
} from 'chart.js';
import { Radar } from 'react-chartjs-2';
import html2canvas from 'html2canvas';
import AICoachChat from './AICoachChat';
import ShareCard from './ShareCard';

ChartJS.register(
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
);

const AnalysisResult = ({ result, duration }) => {
  const { t, language } = useLanguage();
  const [zoomedImage, setZoomedImage] = useState(null);
  const [isExpanded, setIsExpanded] = useState(false);
  const cardRef = React.useRef(null);
  
  if (!result || !result.result) return null;
  const data = result.result; // The Pydantic model dump
  const taskId = result.task_id;

  const handleShare = async () => {
    if (!cardRef.current) return;
    
    try {
        const canvas = await html2canvas(cardRef.current, {
            scale: 2, // High resolution
            useCORS: true,
            backgroundColor: null
        });
        
        const image = canvas.toDataURL("image/png");
        const link = document.createElement('a');
        link.href = image;
        link.download = `ShuttleCoach_${taskId.slice(0,8)}.png`;
        link.click();
    } catch (e) {
        console.error("Share generation failed", e);
        alert(t('share_error') || "Failed to generate image");
    }
  };

  // Prepare Radar Chart Data
  const metricLabels = Object.keys(data.metrics).map(k => t(k));
  const metricValues = Object.values(data.metrics).map(v => v * 100); // Scale to 0-100

  const chartData = {
    labels: metricLabels,
    datasets: [
      {
        label: t('my_performance'),
        data: metricValues,
        backgroundColor: 'rgba(54, 162, 235, 0.2)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 2,
      },
    ],
  };

  const chartOptions = {
    scales: {
      r: {
        angleLines: {
          display: true
        },
        suggestedMin: 0,
        suggestedMax: 100,
        ticks: {
            stepSize: 20
        }
      }
    },
    plugins: {
      legend: {
        display: false 
      }
    }
  };

  return (
    <div style={styles.container}>
      {/* 1. Header & Score */}
      <div style={styles.header}>
        <h1>{data.score} {t('score_suffix')}</h1>
        
        {/* Collapsible Feedback Text */}
        <div style={styles.feedbackContainer}>
            <p style={{
                ...styles.feedback,
                display: '-webkit-box',
                WebkitLineClamp: isExpanded ? 'unset' : 3,
                WebkitBoxOrient: 'vertical',
                overflow: 'hidden'
            }}>
                {data.positive_feedback[language] || data.positive_feedback['zh']}
            </p>
            <button 
                onClick={() => setIsExpanded(!isExpanded)}
                style={styles.expandButton}
            >
                {isExpanded ? (language === 'zh' ? '收起' : 'Show Less') : (language === 'zh' ? '查看更多' : 'Read More')}
            </button>
        </div>

        <span style={styles.badge}>{t(data.action)} | {t(data.level_assumption)}</span>
        
        {/* AI Badge */}
        {data.generation_source === 'gemini' && (
            <span style={{
                ...styles.badge, 
                backgroundColor: '#7b1fa2', 
                marginLeft: '8px',
                backgroundImage: 'linear-gradient(45deg, #7b1fa2, #ab47bc)',
                boxShadow: '0 2px 4px rgba(0,0,0,0.2)'
            }}>
                ⚡ AI Coach
            </span>
        )}
        
        {duration && <p style={styles.duration}>{t('analysis_time')}: {duration} {t('seconds')}</p>}
      </div>

      {/* 2. Radar Chart Visualization */}
      <div style={styles.chartSection}>
        <Radar data={chartData} options={chartOptions} />
      </div>

      {/* 2.5 Keyframe Snapshot or Sequence */}
      {(data.action_sequence && data.action_sequence.length > 0) ? (
        <div style={styles.section}>
            <h3 style={{textAlign: 'center'}}>🎞️ {t('key_moment')}</h3>
            <div style={styles.sequenceContainer}>
                {data.action_sequence.map((img, idx) => (
                    <div key={idx} style={styles.sequenceItem}>
                        <img 
                            src={img} 
                            alt={`Sequence ${idx+1}`} 
                            style={{...styles.keyframeImage, cursor: 'zoom-in'}} 
                            onClick={() => setZoomedImage(img)}
                        />
                        <p style={{textAlign: 'center', fontSize: '12px', color: '#666', marginTop: '4px'}}>
                            {idx === 0 ? t('prep') : (idx === 1 ? t('hit') : t('finish'))}
                        </p>
                    </div>
                ))}
            </div>
        </div>
      ) : (data.keyframe_base64 && (
        <div style={styles.section}>
            <h3 style={{textAlign: 'center'}}>📸 {t('key_moment')}</h3>
            <div style={styles.imageContainer}>
                <img 
                    src={data.keyframe_base64} 
                    alt="Key Moment" 
                    style={{...styles.keyframeImage, cursor: 'zoom-in'}} 
                    onClick={() => setZoomedImage(data.keyframe_base64)}
                />
            </div>
        </div>
      ))}

      {/* Image Modal */}
      {zoomedImage && (
        <div style={styles.modalOverlay} onClick={() => setZoomedImage(null)}>
            <div style={styles.modalContent}>
                <img src={zoomedImage} alt="Zoomed" style={styles.modalImage} />
                <button style={styles.closeModalButton} onClick={() => setZoomedImage(null)}>×</button>
            </div>
        </div>
      )}

      {/* 3. Key Issues */}
      <div style={styles.section}>
        <h3>⚠️ {t('key_issues')}</h3>
        {data.issues.length === 0 ? (
          <p>{t('no_issues')}</p>
        ) : (
          <div style={styles.issueList}>
            {data.issues.map((issue, idx) => (
              <div key={idx} style={styles.issueCard}>
                <div style={styles.issueTag}>{issue.tag}</div>
                <p><strong>{t('coach_tip')}：</strong>{issue.coach_tip[language] || issue.coach_tip['zh']}</p>
                <p><strong>{t('suggestion')}：</strong>{issue.suggestion[language] || issue.suggestion['zh']}</p>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 4. Training Focus */}
      <div style={styles.section}>
        <h3>🎯 {t('training_focus')}</h3>
        <ul>
          {data.next_training_focus.map((item, idx) => (
            <li key={idx}>{item[language] || item['zh']}</li>
          ))}
        </ul>
      </div>

      {/* 5. Detailed Metrics (Table view as backup) */}
      <div style={styles.section}>
        <h3>📊 {t('detailed_metrics')}</h3>
        <div style={styles.metricsGrid}>
          {Object.entries(data.metrics).map(([key, val]) => (
            <div key={key} style={styles.metricItem}>
              <div style={styles.metricLabel}>
                <span>{t(key)}</span>
                <span style={styles.metricValue}>{(val * 100).toFixed(0)}</span>
              </div>
              <div style={styles.progressBarContainer}>
                <div 
                  style={{
                    ...styles.progressBarFill, 
                    width: `${val * 100}%`,
                    backgroundColor: val > 0.7 ? '#4caf50' : (val > 0.4 ? '#ff9800' : '#f44336')
                  }} 
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Share Button */}
      <div style={{textAlign: 'center', margin: '40px 0'}}>
        <button onClick={handleShare} style={styles.shareButton}>
            📤 {t('share_result')}
        </button>
      </div>
      
      {/* Hidden Share Card */}
      <ShareCard data={data} cardRef={cardRef} />

      {/* AI Coach Chat */}
      <AICoachChat taskId={taskId} result={data} />
    </div>
  );
};

const styles = {
  container: {
    maxWidth: '800px',
    margin: '0 auto',
    padding: '20px',
    fontFamily: 'sans-serif'
  },
  header: {
    textAlign: 'center',
    marginBottom: '30px',
    padding: '20px',
    backgroundColor: '#e3f2fd',
    borderRadius: '10px'
  },
  feedback: {
    fontSize: '1.1em',
    color: '#333',
    margin: '0',
    lineHeight: '1.5'
  },
  feedbackContainer: {
    margin: '15px 0',
    textAlign: 'left'
  },
  expandButton: {
    background: 'none',
    border: 'none',
    color: '#1976d2',
    cursor: 'pointer',
    padding: '5px 0',
    fontSize: '0.9em',
    marginTop: '5px',
    fontWeight: '500'
  },
  badge: {
    display: 'inline-block',
    padding: '4px 12px',
    backgroundColor: '#1976d2',
    color: 'white',
    borderRadius: '16px',
    fontSize: '0.9em'
  },
  section: {
    marginBottom: '30px'
  },
  chartSection: {
    marginBottom: '30px',
    maxWidth: '500px',
    margin: '0 auto 30px auto'
  },
  issueList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '15px'
  },
  issueCard: {
    border: '1px solid #ffccbc',
    backgroundColor: '#fff3e0',
    padding: '15px',
    borderRadius: '8px'
  },
  issueTag: {
    fontWeight: 'bold',
    color: '#d84315',
    marginBottom: '5px'
  },
  metricsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
    gap: '12px'
  },
  metricItem: {
    padding: '12px',
    backgroundColor: '#f9f9f9',
    borderRadius: '8px',
    border: '1px solid #eee',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'space-between'
  },
  metricLabel: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: '8px',
    fontWeight: '500',
    fontSize: '0.9em',
    minHeight: '2.4em', // Fix height for 2 lines of text
    lineHeight: '1.2'
  },
  metricValue: {
    fontWeight: 'bold',
    color: '#555'
  },
  progressBarContainer: {
    width: '100%',
    height: '8px',
    backgroundColor: '#e0e0e0',
    borderRadius: '4px',
    overflow: 'hidden'
  },
  progressBarFill: {
    height: '100%',
    borderRadius: '4px',
    transition: 'width 0.5s ease-in-out'
  },
  duration: {
    fontSize: '0.85em',
    color: '#777',
    marginTop: '8px'
  },
  imageContainer: {
    textAlign: 'center',
    margin: '10px 0',
    backgroundColor: '#eee',
    borderRadius: '8px',
    overflow: 'hidden',
    padding: '10px'
  },
  sequenceContainer: {
    display: 'flex',
    justifyContent: 'space-between',
    gap: '8px',
    margin: '10px 0',
    overflowX: 'auto'
  },
  sequenceItem: {
    flex: 1,
    minWidth: '100px',
    backgroundColor: '#eee',
    borderRadius: '8px',
    padding: '8px',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center'
  },
  keyframeImage: {
    maxWidth: '100%',
    height: 'auto',
    display: 'block',
    margin: '0 auto',
    borderRadius: '4px'
  },
  modalOverlay: {
    position: 'fixed',
    top: 0,
    left: 0,
    width: '100%',
    height: '100%',
    backgroundColor: 'rgba(0, 0, 0, 0.85)',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 2000,
    cursor: 'zoom-out'
  },
  modalContent: {
    position: 'relative',
    maxWidth: '90%',
    maxHeight: '90%'
  },
  modalImage: {
    maxWidth: '100%',
    maxHeight: '90vh',
    borderRadius: '4px',
    boxShadow: '0 4px 12px rgba(0,0,0,0.5)'
  },
  closeModalButton: {
    position: 'absolute',
    top: '-40px',
    right: '0',
    background: 'none',
    border: 'none',
    color: 'white',
    fontSize: '30px',
    cursor: 'pointer'
  },
  shareButton: {
    padding: '12px 30px',
    fontSize: '16px',
    fontWeight: 'bold',
    color: 'white',
    backgroundColor: '#ff9800', // Orange
    border: 'none',
    borderRadius: '25px',
    cursor: 'pointer',
    boxShadow: '0 4px 6px rgba(0,0,0,0.2)',
    transition: 'transform 0.1s',
  }
};

export default AnalysisResult;
