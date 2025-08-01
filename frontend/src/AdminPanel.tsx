import React, { useEffect, useState } from 'react';
import './AdminPanel.css';
import { Link } from 'react-router-dom';

interface Site {
    url: string;
    scraped_at: string;
}

export default function AdminPanel() {
    const [sites, setSites] = useState<Site[]>([]);
    const [darkMode, setDarkMode] = useState(true);

    useEffect(() => {
        async function fetchSites() {
            try {
                const res = await fetch('http://localhost:8000/admin/sites', {
                    headers: {
                        Authorization: `Bearer ${localStorage.getItem('token')}`,
                    },
                });
                if (res.ok) {
                    const data = await res.json();
                    setSites(data);
                } else {
                    console.error('Erro ao buscar sites do admin');
                }
            } catch (err) {
                console.error('Erro na requisição admin:', err);
            }
        }
        fetchSites();
    }, []);

    return (
        <div className={`admin-panel-wrapper ${darkMode ? 'dark' : ''}`}>
            <header className="admin-header">
                <h1 className="admin-title">Painel Admin - Sites Scrapeados</h1>

                <div className="admin-header-buttons">
                    <Link to="/" className="admin-back-button">
                        ← Voltar
                    </Link>
                    <button
                        onClick={() => setDarkMode(!darkMode)}
                        className="admin-mode-toggle"
                        aria-label="Alternar modo claro/escuro"
                    >
                        {darkMode ? '☀️' : '🌙'}
                    </button>
                </div>
            </header>

            <main className="admin-main">
                {sites.length === 0 ? (
                    <p className="admin-empty-message">Nenhum site registrado ainda.</p>
                ) : (
                    <ul className="admin-site-list">
                        {sites.map((site) => (
                            <li key={site.url}>
                                {site.url} - {new Date(site.scraped_at).toLocaleString()}
                            </li>
                        ))}
                    </ul>
                )}
            </main>
        </div>
    );
}
