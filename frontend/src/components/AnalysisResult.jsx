import React from 'react';
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
  
  if (!result || !result.result) return null;
  const data = result.result; // The Pydantic model dump

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
        <p style={styles.feedback}>{data.positive_feedback[language] || data.positive_feedback['zh']}</p>
        <span style={styles.badge}>{t(data.action)} | {t(data.level_assumption)}</span>
        {duration && <p style={styles.duration}>{t('analysis_time')}: {duration} {t('seconds')}</p>}
      </div>

      {/* 2. Radar Chart Visualization */}
      <div style={styles.chartSection}>
        <Radar data={chartData} options={chartOptions} />
      </div>

      {/* 2.5 Keyframe Snapshot */}
      {data.keyframe_base64 && (
        <div style={styles.section}>
            <h3 style={{textAlign: 'center'}}>📸 {t('key_moment')}</h3>
            <div style={styles.imageContainer}>
                <img src={data.keyframe_base64} alt="Key Moment" style={styles.keyframeImage} />
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
    fontSize: '1.2em',
    color: '#333',
    margin: '10px 0'
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
  keyframeImage: {
    maxWidth: '100%',
    height: 'auto',
    display: 'block',
    margin: '0 auto',
    borderRadius: '4px'
  }
};

export default AnalysisResult;
