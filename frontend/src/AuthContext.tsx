import React, { createContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';

interface User {
    username: string;
    is_admin: boolean;
}

interface AuthContextType {
    user: User | null;
    token: string | null;
    login: (username: string, password: string) => Promise<void>;
    logout: () => void;
    register: (username: string, password: string) => Promise<boolean>;
}

export const AuthContext = createContext<AuthContextType>({
    user: null,
    token: null,
    login: async () => { },
    logout: () => { },
    register: async () => false,
});

export const AuthProvider = ({ children }: { children: ReactNode }) => {
    const [user, setUser] = useState<User | null>(null);
    const [token, setToken] = useState<string | null>(null);

    useEffect(() => {
        const storedToken = localStorage.getItem('token');
        const storedUser = localStorage.getItem('user');
        if (storedToken && storedUser) {
            setToken(storedToken);
            setUser(JSON.parse(storedUser));
        }
    }, []);

    const login = async (username: string, password: string) => {
        const res = await fetch('http://localhost:8000/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: new URLSearchParams({ username, password }),
        });

        if (!res.ok) {
            throw new Error('Credenciais inválidas');
        }

        const data = await res.json();
        const token = data.access_token;

        setToken(token);
        localStorage.setItem('token', token);

        const userRes = await fetch('http://localhost:8000/me', {
            headers: { Authorization: `Bearer ${token}` },
        });
        if (!userRes.ok) throw new Error('Erro ao buscar dados do usuário');
        const userData = await userRes.json();

        const user = {
            username: userData.sub,
            is_admin: Boolean(userData.is_admin),
        };

        setUser(user);
        localStorage.setItem('user', JSON.stringify(user));
    };

    // Implementação do register
    const register = async (username: string, password: string): Promise<boolean> => {
        const res = await fetch('http://localhost:8000/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password }),
        });

        return res.ok;
    };

    const logout = () => {
        setUser(null);
        setToken(null);
        localStorage.removeItem('token');
        localStorage.removeItem('user');
    };

    return (
        <AuthContext.Provider value={{ user, token, login, logout, register }}>
            {children}
        </AuthContext.Provider>
    );
};
