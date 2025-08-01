import React, { useState, useEffect, useContext } from 'react';
import './App.css';
import { AuthContext } from './AuthContext';
import { Link } from 'react-router-dom';

export default function Scraper() {
    const [url, setUrl] = useState('');
    const [loading, setLoading] = useState(false);
    const [scrapeData, setScrapeData] = useState<any>(null);
    const [analysis, setAnalysis] = useState<any>(null);
    const [error, setError] = useState('');
    const [showScrape, setShowScrape] = useState(true);
    const [showAnalysis, setShowAnalysis] = useState(true);
    const [darkMode, setDarkMode] = useState(true);
    const { user } = useContext(AuthContext);


    useEffect(() => {
        document.title = 'CaseBNA';
    }, []);

    const handleSubmit = async () => {
        setLoading(true);
        setError('');
        setScrapeData(null);
        setAnalysis(null);

        try {
            const scrapeRes = await fetch('http://localhost:8000/scrape', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url }),
            });

            if (!scrapeRes.ok) throw new Error('Erro ao fazer scrape.');
            const scrapeJson = await scrapeRes.json();
            setScrapeData(scrapeJson.data);

            const analyzeRes = await fetch('http://localhost:8000/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url }),
            });

            if (!analyzeRes.ok) throw new Error('Erro ao fazer análise.');
            const analyzeJson = await analyzeRes.json();
            setAnalysis(analyzeJson.resumo || analyzeJson.summary || analyzeJson);
        } catch (err: any) {
            setError(err.message || 'Erro desconhecido');
        }

        setLoading(false);
    };

    return (
        <div className={darkMode ? 'app dark' : 'app'}>
            <header className="header">
                <h1 className="title">Analisador de Sites</h1>
                {user?.is_admin && (
                    <Link to="/admin" style={{ marginRight: '1rem', color: darkMode ? '#8e4dfb' : '#000' }}>
                        Painel Admin
                    </Link>
                )}
                <button onClick={() => setDarkMode(!darkMode)} className="mode-toggle">
                    {darkMode ? '☀️' : '🌙'}
                </button>
            </header>

            <main className="main">
                <section className="input-section">
                    <input
                        type="text"
                        placeholder="Digite a URL..."
                        value={url}
                        onChange={(e) => setUrl(e.target.value)}
                    />
                    <button onClick={handleSubmit} disabled={loading}>
                        {loading ? 'Processando...' : 'Analisar'}
                    </button>
                    {error && <p className="error">Erro: {error}</p>}
                </section>

                <section className="results">
                    {scrapeData && (
                        <div className="result-block">
                            <div className="result-header">
                                <h2>Dados Extraídos</h2>
                                <button onClick={() => setShowScrape(!showScrape)}>
                                    {showScrape ? 'Esconder' : 'Mostrar'}
                                </button>
                            </div>
                            {showScrape && (
                                <pre className="scroll-box">
                                    {JSON.stringify(scrapeData, null, 2)}
                                </pre>
                            )}
                        </div>
                    )}

                    {analysis && (
                        <div className="result-block">
                            <div className="result-header">
                                <h2>Resumo Comercial</h2>
                                <button onClick={() => setShowAnalysis(!showAnalysis)}>
                                    {showAnalysis ? 'Esconder' : 'Mostrar'}
                                </button>
                            </div>
                            {showAnalysis && (
                                <pre className="scroll-box">
                                    {typeof analysis === 'string'
                                        ? analysis
                                        : JSON.stringify(analysis, null, 2)}
                                </pre>
                            )}
                        </div>
                    )}
                </section>
            </main>
        </div>
    );
}
