import React, { useState, useEffect, useRef } from 'react';
import { useLanguage } from '../LanguageContext';

const TriviaCarousel = () => {
  const { t } = useLanguage();
  const [currentTrivia, setCurrentTrivia] = useState(0);
  const triviaInterval = useRef(null);

  useEffect(() => {
    const list = t('trivia_list');
    if (list && list.length > 0) {
        triviaInterval.current = setInterval(() => {
            setCurrentTrivia(prev => (prev + 1) % list.length);
        }, 4000);
    }
    
    return () => {
        if (triviaInterval.current) clearInterval(triviaInterval.current);
    };
  }, [t]);

  return (
    <div style={styles.triviaContainer}>
        <div style={styles.triviaTitle}>{t('did_you_know')}</div>
        <div style={styles.triviaContent}>
            {t('trivia_list') && t('trivia_list')[currentTrivia]}
        </div>
    </div>
  );
};

const styles = {
  triviaContainer: {
    maxWidth: '400px',
    padding: '15px',
    backgroundColor: '#fff3e0', // Light Orange
    borderRadius: '8px',
    border: '1px solid #ffe0b2',
    textAlign: 'center',
    animation: 'fadeIn 0.5s ease-in-out',
    margin: '20px auto'
  },
  triviaTitle: {
    fontWeight: 'bold',
    color: '#ef6c00',
    marginBottom: '5px',
    fontSize: '0.9em'
  },
  triviaContent: {
    color: '#555',
    fontSize: '0.95em',
    lineHeight: '1.4',
    minHeight: '2.8em' // Prevent jumping
  }
};

export default TriviaCarousel;
