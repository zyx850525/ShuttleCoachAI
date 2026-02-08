import React from 'react';
import { useLanguage } from '../LanguageContext';

const ShareCard = ({ data, cardRef }) => {
  const { t, language } = useLanguage();

  if (!data) return null;

  return (
    <div style={styles.wrapper}>
      {/* 
        This is the card that will be captured. 
        It is rendered off-screen or hidden, but needs to be "visible" to html2canvas.
        We position it absolutely off-screen.
      */}
      <div ref={cardRef} style={styles.card}>
        <div style={styles.header}>
          <div style={styles.title}>🏸 ShuttleCoach AI</div>
          <div style={styles.subtitle}>{t('app_subtitle')}</div>
        </div>

        <div style={styles.scoreSection}>
          <div style={styles.score}>{data.score}</div>
          <div style={styles.scoreLabel}>{t('score_suffix')}</div>
        </div>

        <div style={styles.tagSection}>
          <span style={styles.tag}>{t(data.action)}</span>
          <span style={styles.tag}>{t(data.level_assumption)}</span>
        </div>

        <div style={styles.feedbackSection}>
          <div style={styles.quote}>"</div>
          <div style={styles.feedback}>
            {data.positive_feedback[language] || data.positive_feedback['zh']}
          </div>
          <div style={styles.quote}>"</div>
        </div>

        <div style={styles.metricsSection}>
            {Object.entries(data.metrics).slice(0, 4).map(([key, val]) => (
                <div key={key} style={styles.metricRow}>
                    <span style={styles.metricName}>{t(key)}</span>
                    <div style={styles.metricBarBg}>
                        <div style={{...styles.metricBarFill, width: `${val * 100}%`}}></div>
                    </div>
                </div>
            ))}
        </div>

        <div style={styles.footer}>
          {t('scan_to_try')}
        </div>
      </div>
    </div>
  );
};

const styles = {
  wrapper: {
    position: 'absolute',
    top: '-9999px',
    left: '-9999px',
  },
  card: {
    width: '375px',
    padding: '30px',
    backgroundColor: '#1a237e', // Deep Blue
    color: 'white',
    fontFamily: 'sans-serif',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    backgroundImage: 'linear-gradient(135deg, #1a237e 0%, #283593 100%)',
    borderRadius: '0', // Sharp corners for image
  },
  header: {
    textAlign: 'center',
    marginBottom: '20px',
  },
  title: {
    fontSize: '24px',
    fontWeight: 'bold',
    color: '#ffeb3b', // Yellow
    letterSpacing: '1px',
  },
  subtitle: {
    fontSize: '12px',
    color: '#c5cae9',
    marginTop: '5px',
  },
  scoreSection: {
    textAlign: 'center',
    margin: '10px 0',
    border: '4px solid #ffeb3b',
    borderRadius: '50%',
    width: '120px',
    height: '120px',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
  },
  score: {
    fontSize: '48px',
    fontWeight: 'bold',
    lineHeight: '1',
  },
  scoreLabel: {
    fontSize: '14px',
    marginTop: '5px',
    opacity: 0.8,
  },
  tagSection: {
    display: 'flex',
    gap: '10px',
    marginBottom: '20px',
  },
  tag: {
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    padding: '4px 12px',
    borderRadius: '12px',
    fontSize: '12px',
  },
  feedbackSection: {
    textAlign: 'center',
    marginBottom: '25px',
    position: 'relative',
    padding: '0 20px',
  },
  feedback: {
    fontSize: '14px',
    lineHeight: '1.5',
    fontStyle: 'italic',
  },
  quote: {
    fontSize: '20px',
    color: '#ffeb3b',
    lineHeight: '1',
  },
  metricsSection: {
    width: '100%',
    marginBottom: '30px',
  },
  metricRow: {
    display: 'flex',
    alignItems: 'center',
    marginBottom: '8px',
  },
  metricName: {
    fontSize: '12px',
    width: '100px',
    textAlign: 'right',
    marginRight: '10px',
    whiteSpace: 'nowrap',
    overflow: 'hidden',
    textOverflow: 'ellipsis',
  },
  metricBarBg: {
    flex: 1,
    height: '6px',
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    borderRadius: '3px',
  },
  metricBarFill: {
    height: '100%',
    backgroundColor: '#ffeb3b',
    borderRadius: '3px',
  },
  footer: {
    fontSize: '10px',
    opacity: 0.5,
    marginTop: 'auto',
  },
};

export default ShareCard;
