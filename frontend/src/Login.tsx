import React, { useContext, useState } from 'react';
import './login.css';
import type { FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from './AuthContext';

const Login: React.FC = () => {
    const { login } = useContext(AuthContext);
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const navigate = useNavigate();

    const handleLogin = async (e: FormEvent) => {
        e.preventDefault();
        setError('');
        setSuccess('');

        try {
            await login(username, password);
            setSuccess('Login realizado com sucesso! Redirecionando...');
            setTimeout(() => {
                navigate('/'); // Vai para home
            }, 1500);
        } catch (err: unknown) {
            if (err instanceof Error) {
                setError(err.message);
            } else {
                setError('Erro ao fazer login.');
            }
        }
    };

    return (
        <div className="auth-wrapper">
            <div className="auth-box">
                <h2>Login</h2>
                <form onSubmit={handleLogin}>
                    <input
                        type="text"
                        placeholder="Usuário"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        required
                        autoFocus
                    />
                    <input
                        type="password"
                        placeholder="Senha"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                    />
                    <button type="submit">Entrar</button>
                </form>
                {error && <p className="error">{error}</p>}
                {success && <p className="success">{success}</p>}
                <div className="auth-links">
                    <a href="/scraper">Analisar URL</a>
                    <a href="/admin">Painel Admin</a>
                    <a href="/register">Registrar</a>
                </div>
            </div>
        </div>
    );
};

export default Login;
