import React, { useEffect, useState } from 'react';

interface Site {
    url: string;
    scraped_at: string;
}

export default function AdminPanel() {
    const [sites, setSites] = useState<Site[]>([]);

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
        <div className="admin-panel">
            <h2>Painel Admin - Sites Scrapeados</h2>
            {sites.length === 0 ? (
                <p>Nenhum site registrado ainda.</p>
            ) : (
                <ul>
                    {sites.map((site) => (
                        <li key={site.url}>
                            {site.url} - {new Date(site.scraped_at).toLocaleString()}
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
}
