import React, { useState, useEffect } from 'react';
import { useLanguage } from '../LanguageContext';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const GrowthProfile = ({ onClose }) => {
  const { t, language } = useLanguage();
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/history')
      .then(res => res.json())
      .then(data => {
        setHistory(data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to fetch history', err);
        setLoading(false);
      });
  }, []);

  // Prepare Chart Data
  // Reverse history for chronological order in chart
  const chartHistory = [...history].reverse();
  const labels = chartHistory.map(item => {
      const date = new Date(item.created_at);
      return `${date.getMonth()+1}/${date.getDate()}`;
  });
  
  const scores = chartHistory.map(item => item.result ? item.result.score : 0);

  const chartData = {
    labels,
    datasets: [
      {
        label: t('score_history'),
        data: scores,
        borderColor: 'rgb(255, 99, 132)',
        backgroundColor: 'rgba(255, 99, 132, 0.5)',
        tension: 0.3
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: t('growth_trend'),
      },
    },
    scales: {
        y: {
            min: 0,
            max: 100
        }
    }
  };

  return (
    <div style={styles.overlay}>
      <div style={styles.modal}>
        <div style={styles.header}>
          <h2>📈 {t('growth_profile')}</h2>
          <button onClick={onClose} style={styles.closeButton}>×</button>
        </div>

        {loading ? (
          <p>{t('loading_history')}</p>
        ) : (
          <div style={styles.content}>
            {/* Chart Section */}
            {history.length > 1 && (
                <div style={styles.chartContainer}>
                    <Line options={chartOptions} data={chartData} />
                </div>
            )}

            {/* List Section */}
            <div style={styles.listContainer}>
                <h3>{t('history_records')}</h3>
                {history.length === 0 ? (
                    <p style={{color: '#666'}}>{t('no_history')}</p>
                ) : (
                    history.map(item => {
                        const res = item.result;
                        if (!res) return null;
                        const date = new Date(item.created_at).toLocaleDateString();
                        return (
                            <div key={item.task_id} style={styles.historyItem}>
                                <div style={styles.itemHeader}>
                                    <span style={styles.itemAction}>{t(res.action)}</span>
                                    <span style={styles.itemScore}>{res.score} {t('score_suffix')}</span>
                                </div>
                                <div style={styles.itemDate}>{date}</div>
                                <div style={styles.itemFeedback}>
                                    {res.positive_feedback && (res.positive_feedback[language] || res.positive_feedback['zh'])}
                                </div>
                            </div>
                        );
                    })
                )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

const styles = {
  overlay: {
    position: 'fixed',
    top: 0,
    left: 0,
    width: '100%',
    height: '100%',
    backgroundColor: 'rgba(0,0,0,0.5)',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 1000
  },
  modal: {
    backgroundColor: 'white',
    borderRadius: '12px',
    width: '90%',
    maxWidth: '600px',
    maxHeight: '85vh',
    display: 'flex',
    flexDirection: 'column',
    boxShadow: '0 4px 20px rgba(0,0,0,0.2)',
    overflow: 'hidden'
  },
  header: {
    padding: '20px',
    borderBottom: '1px solid #eee',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center'
  },
  closeButton: {
    background: 'none',
    border: 'none',
    fontSize: '24px',
    cursor: 'pointer'
  },
  content: {
    padding: '20px',
    overflowY: 'auto'
  },
  chartContainer: {
    marginBottom: '30px'
  },
  listContainer: {
    display: 'flex',
    flexDirection: 'column',
    gap: '15px'
  },
  historyItem: {
    padding: '15px',
    backgroundColor: '#f9f9f9',
    borderRadius: '8px',
    border: '1px solid #eee'
  },
  itemHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    fontWeight: 'bold',
    marginBottom: '5px'
  },
  itemAction: {
    color: '#1976d2'
  },
  itemScore: {
    color: '#ff9800'
  },
  itemDate: {
    fontSize: '12px',
    color: '#888',
    marginBottom: '8px'
  },
  itemFeedback: {
    fontSize: '14px',
    color: '#333',
    display: '-webkit-box',
    WebkitLineClamp: 2,
    WebkitBoxOrient: 'vertical',
    overflow: 'hidden'
  }
};

export default GrowthProfile;
