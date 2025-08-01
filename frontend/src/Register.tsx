import React, { useState, useContext } from 'react';
import './register.css';
import type { FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from './AuthContext';

export default function Register() {
    const { register } = useContext(AuthContext);
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault();
        setError('');
        setSuccess('');

        try {
            const successRegister = await register(username, password);
            if (successRegister) {
                setSuccess('Usuário criado com sucesso! Redirecionando para login...');
                setUsername('');
                setPassword('');
                setTimeout(() => {
                    navigate('/login');
                }, 2000);
            } else {
                setError('Erro ao criar usuário. Talvez já exista.');
            }
        } catch {
            setError('Erro inesperado ao registrar.');
        }
    };

    return (
        <div className="auth-wrapper">
            <form onSubmit={handleSubmit} className="auth-box">
                <h2>Registrar</h2>
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
                <button type="submit">Registrar</button>
                {error && <p className="error">{error}</p>}
                {success && <p className="success">{success}</p>}
            </form>
        </div>
    );
}
