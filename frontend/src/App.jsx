import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { ChevronRight, Home, ListTodo, Plus, LogOut, Loader2, Trash2, Edit, CheckCircle, Clock, Check, BarChart3, Users, Mail, Lock } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, XAxis, YAxis, Tooltip, Bar, CartesianGrid } from 'recharts';
import api from './api';

const COLORS = {
    primary: '#6B21A8',
    secondary: '#2DD4BF',
    pending: '#FCD34D',
    completed: '#2DD4BF',
    text: '#1F2937',
};

const Button = ({ children, onClick, variant = 'primary', icon: Icon, className = '', disabled = false, type = 'button' }) => {
    const baseStyle = 'flex items-center justify-center font-semibold rounded-lg transition-colors duration-200 shadow-md focus:outline-none focus:ring-2 focus:ring-offset-2';
    let variantStyle = '';

    switch (variant) {
        case 'primary':
            variantStyle = `bg-violet-700 text-white hover:bg-violet-800 focus:ring-violet-500 ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`;
            break;
        case 'secondary':
            variantStyle = `bg-gray-200 text-gray-700 hover:bg-gray-300 focus:ring-gray-400 ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`;
            break;
        case 'danger':
            variantStyle = `bg-transparent text-red-500 hover:bg-red-50 border border-red-500 focus:ring-red-500 ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`;
            break;
        case 'success':
            variantStyle = `bg-emerald-500 text-white hover:bg-emerald-600 focus:ring-emerald-400 ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`;
            break;
    }

    return (
        <button type={type} className={`${baseStyle} ${variantStyle} ${className} px-4 py-2`} onClick={!disabled ? onClick : undefined} disabled={disabled}>
            {Icon && <Icon className="w-5 h-5 mr-2" />}
            {children}
        </button>
    );
};

const Input = React.forwardRef(({ label, type = 'text', value, onChange, placeholder, className = '', icon: Icon, required = false }, ref) => (
    <div className="flex flex-col space-y-1 w-full">
        {label && <label className="text-sm font-medium text-gray-700">{label}</label>}
        <div className="relative">
            {Icon && <Icon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />}
            <input ref={ref} type={type} value={value} onChange={onChange} placeholder={placeholder} required={required} className={`w-full border border-gray-300 rounded-lg p-3 text-gray-900 focus:border-violet-500 focus:ring-1 focus:ring-violet-500 transition duration-150 ${Icon ? 'pl-10' : 'pl-4'} ${className}`} />
        </div>
    </div>
));

const Card = ({ children, className = '' }) => (
    <div className={`bg-white p-6 rounded-xl shadow-lg border border-gray-100 ${className}`}>
        {children}
    </div>
);

const ProgressRing = ({ percent, pendingPercent }) => {
    const data = useMemo(() => ([
        { name: 'Concluídas', value: percent, color: COLORS.completed },
        { name: 'Pendentes', value: pendingPercent, color: COLORS.pending },
    ]), [percent, pendingPercent]);

    return (
        <div className="flex flex-col items-center">
            <div className="w-40 h-40">
                <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                        <Pie data={data} cx="50%" cy="50%" innerRadius={55} outerRadius={70} paddingAngle={0} dataKey="value" startAngle={90} endAngle={450}>
                            {data.map((entry, index) => (<Cell key={`cell-${index}`} fill={entry.color} />))}
                        </Pie>
                    </PieChart>
                </ResponsiveContainer>
            </div>
            <div className="flex justify-center space-x-4 mt-4 text-sm">
                <div className="flex items-center"><span className="w-3 h-3 rounded-full mr-2" style={{ backgroundColor: COLORS.pending }}></span><span>Pendentes ({pendingPercent}%)</span></div>
                <div className="flex items-center"><span className="w-3 h-3 rounded-full mr-2" style={{ backgroundColor: COLORS.completed }}></span><span>Concluídas ({percent}%)</span></div>
            </div>
        </div>
    );
};

const WeeklyActivityChart = ({ tasks }) => {
    const mockData = useMemo(() => {
        const days = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'];
        const today = new Date();
        const mockCounts = Array(7).fill(0).map((_, i) => {
            const dayIndex = (today.getDay() + i + 1) % 7;
            let count = dayIndex >= 1 && dayIndex <= 5 ? Math.floor(Math.random() * 8) + 5 : Math.floor(Math.random() * 5) + 1;
            return { name: days[dayIndex], Tarefas: count };
        });
        const relevantDays = mockCounts.filter(d => d.name !== 'Dom').slice(0, 6);
        const colors = ['#6B21A8', '#6B21A8', '#6B21A8', '#6B21A8', '#2DD4BF', '#6B21A8'];
        return relevantDays.map((data, index) => ({ ...data, color: colors[index] }));
    }, [tasks]);

    return (
        <ResponsiveContainer width="100%" height={250}>
            <BarChart data={mockData} margin={{ top: 10, right: 0, left: -20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E5E7EB" />
                <XAxis dataKey="name" stroke="#6B21A8" tickLine={false} axisLine={false} />
                <YAxis stroke="#6B21A8" tickLine={false} axisLine={false} allowDecimals={false} />
                <Tooltip contentStyle={{ backgroundColor: 'white', border: '1px solid #ccc', borderRadius: '8px', padding: '10px' }} labelStyle={{ fontWeight: 'bold', color: COLORS.text }} formatter={(value) => [`${value} tarefas`, '']} />
                <Bar dataKey="Tarefas" radius={[10, 10, 0, 0]}>{mockData.map((entry, index) => (<Cell key={`cell-${index}`} fill={entry.color} />))}</Bar>
            </BarChart>
        </ResponsiveContainer>
    );
};

// Usaremos a API (JWT) para autenticação e persistência de tarefas.

const useTasks = (isLoggedIn, user) => {
    const [tasks, setTasks] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        let mounted = true;
        const load = async () => {
            if (!isLoggedIn || !user) { setTasks([]); return; }
            setLoading(true); setError(null);
            try {
                const data = await api.listTasks();
                // api.listTasks returns an array of tarefas
                const mapped = (Array.isArray(data) ? data : []).map(t => ({
                    id: t.id,
                    title: t.titulo,
                    description: t.descricao,
                    completed: t.status === 'CONCLUIDA',
                    createdAt: t.data_criacao ? new Date(t.data_criacao) : new Date()
                }));
                if (mounted) setTasks(mapped);
            } catch (err) {
                setError(err.message || 'Falha ao carregar tarefas');
            } finally {
                if (mounted) setLoading(false);
            }
        };
        load();
        return () => { mounted = false; };
    }, [isLoggedIn, user]);

    const addTask = useCallback(async (title, description) => {
        try {
            const created = await api.createTask({ titulo: title, descricao: description });
            const mapped = { id: created.id, title: created.titulo, description: created.descricao, completed: created.status === 'CONCLUIDA', createdAt: created.data_criacao ? new Date(created.data_criacao) : new Date() };
            setTasks(prev => [mapped, ...(prev || [])]);
        } catch (err) { throw err; }
    }, []);

    const toggleTask = useCallback(async (taskId, completed) => {
        try {
            const status = completed ? 'CONCLUIDA' : 'PENDENTE';
            const updated = await api.updateTask(taskId, { status });
            setTasks(prev => (prev || []).map(t => t.id === taskId ? { ...t, completed: updated.status === 'CONCLUIDA' } : t));
        } catch (err) { throw err; }
    }, []);

    const deleteTask = useCallback(async (taskId) => {
        try {
            await api.deleteTask(taskId);
            setTasks(prev => (prev || []).filter(t => t.id !== taskId));
        } catch (err) { throw err; }
    }, []);

    return { tasks, loading, error, addTask, toggleTask, deleteTask };
};

const LoginPage = ({ onLogin, onSwitchToRegister }) => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');
    const handleAuth = async (e) => {
        e.preventDefault();
        setError('');
        setIsLoading(true);
        try {
            if (!email || !password) throw new Error('Preencha e-mail e senha.');
            // chamar API de login
            await api.login(email, password);
            // obter dados do usuário
            const me = await api.getMe();
            const userObj = Array.isArray(me) && me.length > 0 ? me[0] : me;
            onLogin({ displayName: userObj.first_name || (userObj.email || '').split('@')[0], email: userObj.email });
        } catch (err) {
            setError(err.message || 'Erro ao autenticar.');
            setIsLoading(false);
        }
    };
    const handleSwitchToRegister = (e) => {
        // prevenir comportamento de link/form
        if (e && e.preventDefault) e.preventDefault();
        if (typeof onSwitchToRegister === 'function') onSwitchToRegister();
    };
    return (
        <div className="min-h-screen flex">
            <div className="w-1/2 bg-gray-900 flex flex-col items-center justify-center p-12 text-white" style={{ background: 'linear-gradient(135deg, #1F1B24 0%, #3B0068 100%)' }}>
                <h1 className="text-5xl font-extrabold text-center mb-4">Organize seu dia.</h1>
                <p className="text-xl text-center text-gray-300 max-w-sm">Concentre-se no que realmente importa e alcance suas metas com mais clareza.</p>
            </div>
            <div className="w-1/2 flex items-center justify-center bg-white">
                <Card className="max-w-md w-full p-8 shadow-xl">
                    <h2 className="text-3xl font-bold mb-2 text-gray-900">Checklist</h2>
                    <p className="text-gray-500 mb-8">Faça login na sua conta para continuar.</p>
                    <form onSubmit={handleAuth} className="space-y-6">
                        <Input label="E-mail" type="email" placeholder="seu@email.com" value={email} onChange={(e) => setEmail(e.target.value)} icon={Mail} required />
                        <Input label="Senha" type="password" placeholder="••••••••" value={password} onChange={(e) => setPassword(e.target.value)} icon={Lock} required />
                        <div className="flex justify-end text-sm">
                            <button type="button" onClick={async (e) => {
                                if (e && e.preventDefault) e.preventDefault();
                                try {
                                    const email = window.prompt('Informe seu e-mail para receber instruções de redefinição:');
                                    if (!email) return;
                                    await api.requestPasswordReset(email);
                                    alert('Se um usuário com este e-mail existir, um email com instruções foi enviado (simulado).');
                                } catch (err) {
                                    alert(err.message || 'Falha ao solicitar redefinição de senha.');
                                }
                            }} className="text-violet-700 hover:text-violet-800 font-medium">Esqueceu a senha?</button>
                        </div>
                        {error && <p className="text-red-500 text-sm text-center">{error}</p>}
                        <div className="flex space-x-3">
                            <Button type="submit" variant="primary" className="w-full py-3" disabled={isLoading}>{isLoading ? <Loader2 className="animate-spin mr-2 w-5 h-5" /> : null}Entrar</Button>
                            <Button type="button" variant="secondary" onClick={handleSwitchToRegister}>Cadastrar</Button>
                        </div>
                    </form>
                </Card>
            </div>
        </div>
    );
};

const RegistrationPage = ({ onRegister, onSwitchToLogin }) => {
    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirm, setConfirm] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleRegister = async (e) => {
        e.preventDefault();
        setError('');
        if (!email || !password) { setError('Preencha e-mail e senha.'); return; }
        if (password !== confirm) { setError('Senhas não conferem.'); return; }
        setLoading(true);
        try {
            // registrar via API
            await api.register({ email, first_name: name || email.split('@')[0], password });
            // auto-login
            await api.login(email, password);
            const me = await api.getMe();
            const userObj = Array.isArray(me) && me.length > 0 ? me[0] : me;
            setLoading(false);
            onRegister({ displayName: userObj.first_name || (userObj.email || '').split('@')[0], email: userObj.email });
        } catch (err) {
            setError(err.data && err.data.email ? (Array.isArray(err.data.email) ? err.data.email.join(', ') : err.data.email) : (err.message || 'Falha ao criar conta'));
            setLoading(false);
        }
    };

    const handleSwitchToLogin = (e) => {
        if (e && e.preventDefault) e.preventDefault();
        if (typeof onSwitchToLogin === 'function') onSwitchToLogin();
    };

    return (
        <div className="min-h-screen flex">
            <div className="w-1/2 bg-gray-900 flex flex-col items-center justify-center p-12 text-white" style={{ background: 'linear-gradient(135deg, #1F1B24 0%, #3B0068 100%)' }}>
                <h1 className="text-5xl font-extrabold text-center mb-4">Comece agora.</h1>
                <p className="text-xl text-center text-gray-300 max-w-sm">Crie sua conta e organize suas tarefas.</p>
            </div>
            <div className="w-1/2 flex items-center justify-center bg-white">
                <Card className="max-w-md w-full p-8 shadow-xl">
                    <h2 className="text-3xl font-bold mb-2 text-gray-900">Criar conta</h2>
                    <p className="text-gray-500 mb-8">Preencha os dados para criar sua conta.</p>
                    <form onSubmit={handleRegister} className="space-y-6">
                        <Input label="Nome" value={name} onChange={(e) => setName(e.target.value)} placeholder="Seu nome" />
                        <Input label="E-mail" type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="seu@email.com" icon={Mail} required />
                        <Input label="Senha" type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="••••••••" icon={Lock} required />
                        <Input label="Confirmar senha" type="password" value={confirm} onChange={(e) => setConfirm(e.target.value)} placeholder="••••••••" required />
                        {error && <p className="text-red-500 text-sm text-center">{error}</p>}
                        <div className="flex space-x-3">
                            <Button type="submit" variant="primary" className="w-full py-3" disabled={loading}>{loading ? 'Criando...' : 'Criar conta'}</Button>
                            <Button type="button" variant="secondary" onClick={handleSwitchToLogin}>Voltar</Button>
                        </div>
                    </form>
                </Card>
            </div>
        </div>
    );
};

const DashboardPage = ({ user, tasks, goToTasks, onLogout }) => {
    const totalTasks = tasks.length;
    const completedTasks = tasks.filter(t => t.completed).length;
    const pendingTasks = totalTasks - completedTasks;
    const percentCompleted = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;
    const percentPending = 100 - percentCompleted;
    const CardStat = ({ title, value, icon: Icon, color }) => (
        <Card className="flex flex-col items-center p-4 text-center">
            <div className={`flex items-center justify-center w-12 h-12 rounded-full mb-3`} style={{ backgroundColor: `${color}1A`, color: color }}>
                <Icon className="w-6 h-6" />
            </div>
            <p className="text-gray-500 text-sm">{title}</p>
            <p className="text-3xl font-bold text-gray-800 mt-1">{value}</p>
        </Card>
    );
    return (
        <div className="p-8 space-y-8">
            <Header user={user} goToTasks={goToTasks} onLogout={onLogout} activePage="Home" />
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <CardStat title="Total de Tarefas" value={totalTasks} icon={ListTodo} color={COLORS.primary} />
                <CardStat title="Tarefas Pendentes" value={pendingTasks} icon={Clock} color={COLORS.pending} />
                <CardStat title="Tarefas Concluídas" value={completedTasks} icon={CheckCircle} color={COLORS.completed} />
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card><h3 className="text-xl font-semibold mb-4 text-gray-800">Progresso Geral</h3><ProgressRing percent={percentCompleted} pendingPercent={percentPending} /></Card>
                <Card><h3 className="text-xl font-semibold mb-4 text-gray-800">Atividade da Semana</h3><WeeklyActivityChart tasks={tasks} /></Card>
            </div>
        </div>
    );
};

const TasksPage = ({ user, tasks, loading, error, addTask, toggleTask, deleteTask, goToHome, onLogout }) => {
    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');
    const [filter, setFilter] = useState('Todas');
    const [isAdding, setIsAdding] = useState(false);
    const handleAddTask = async (e) => {
        e.preventDefault();
        if (!title.trim()) return;
        setIsAdding(true);
        await addTask(title, description);
        setTitle('');
        setDescription('');
        setIsAdding(false);
    };
    const filteredTasks = useMemo(() => {
        switch (filter) {
            case 'Pendentes': return tasks.filter(t => !t.completed);
            case 'Concluídas': return tasks.filter(t => t.completed);
            default: return tasks;
        }
    }, [tasks, filter]);
    const completedCount = tasks.filter(t => t.completed).length;
    const totalCount = tasks.length;
    return (
        <div className="p-8 space-y-8 min-h-screen">
            <Header user={user} goToHome={goToHome} onLogout={onLogout} activePage="Tarefas" />
            <Card className="max-w-3xl mx-auto p-8 space-y-6">
                <h2 className="text-2xl font-bold text-gray-900 text-center">Minhas Tarefas</h2>
                <div className="bg-gray-50 p-6 rounded-xl border border-gray-100">
                    <h3 className="text-xl font-semibold mb-4 text-gray-800">Adicionar nova tarefa</h3>
                    <form onSubmit={handleAddTask} className="space-y-4">
                        <Input type="text" placeholder="Título da tarefa" value={title} onChange={(e) => setTitle(e.target.value)} required className="p-3" />
                        <textarea placeholder="Descrição..." value={description} onChange={(e) => setDescription(e.target.value)} rows="3" className="w-full border border-gray-300 rounded-lg p-3 text-gray-900 focus:border-violet-500 focus:ring-1 focus:ring-violet-500 transition duration-150 resize-none" />
                        <Button type="submit" variant="success" icon={Plus} className="w-full py-3" disabled={!title.trim() || isAdding}>{isAdding ? 'Adicionando...' : 'Adicionar Tarefa'}</Button>
                    </form>
                </div>
                <div className="flex justify-between items-center pt-4 border-t border-gray-100">
                    <div className="flex space-x-2">
                        {['Todas', 'Pendentes', 'Concluídas'].map(f => (<button key={f} onClick={() => setFilter(f)} className={`px-4 py-2 text-sm font-semibold rounded-lg transition-colors duration-150 ${filter === f ? 'bg-violet-700 text-white shadow-md' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`}>{f}</button>))}
                    </div>
                    <p className="text-sm text-gray-600">{completedCount} de {totalCount} tarefas concluídas</p>
                </div>
                {loading && <div className="text-center text-gray-500 flex items-center justify-center py-8"><Loader2 className="animate-spin mr-2" /> Carregando tarefas...</div>}
                {error && <div className="text-center text-red-500 py-8">{error}</div>}
                {!loading && filteredTasks.length === 0 && (<div className="text-center text-gray-500 py-8 border-t border-gray-100">Nenhuma tarefa {filter.toLowerCase()}. Adicione uma nova!</div>)}
                <div className="space-y-4">
                    {filteredTasks.map(task => (<TaskItem key={task.id} task={task} toggleTask={toggleTask} deleteTask={deleteTask} />))}
                </div>
            </Card>
        </div>
    );
};

const TaskItem = ({ task, toggleTask, deleteTask }) => {
    const [isDeleting, setIsDeleting] = useState(false);
    const handleToggle = () => toggleTask(task.id, !task.completed);
    const handleDelete = async () => { setIsDeleting(true); await deleteTask(task.id); };
    const formatDate = (date) => {
        if (!(date instanceof Date) || isNaN(date)) return 'Data desconhecida';
        return date.toLocaleDateString('pt-BR', { day: '2-digit', month: 'short', year: 'numeric' }).replace('.', '');
    };
    return (
        <div className={`flex items-start p-4 rounded-xl border transition-colors duration-200 ${task.completed ? 'border-emerald-100 bg-emerald-50' : 'border-gray-100 bg-white shadow-sm hover:bg-gray-50'}`}>
            <input type="checkbox" checked={task.completed} onChange={handleToggle} className={`mt-1 w-5 h-5 rounded-md appearance-none transition-all duration-300 border-2 ${task.completed ? 'bg-emerald-500 border-emerald-500 checked:text-white' : 'border-gray-300 hover:border-violet-500'} focus:ring-0 cursor-pointer`} style={task.completed ? { backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 20 20' fill='white'%3E%3Cpath fill-rule='evenodd' d='M16.704 4.153a.75.75 0 01.353 1.09l-7 14.5a.75.75 0 01-1.42.062l-3-6a.75.75 0 011.341-.67L9 14.885l6.546-13.565a.75.75 0 011.09-.353z' clip-rule='evenodd' /%3E%3C/svg%3E")`, backgroundPosition: 'center', backgroundRepeat: 'no-repeat', backgroundSize: '1em' } : {}} />
            <div className="ml-4 flex-1">
                <h4 className={`text-lg font-semibold ${task.completed ? 'line-through text-gray-500' : 'text-gray-900'}`}>{task.title}</h4>
                <p className={`text-sm mt-1 ${task.completed ? 'text-gray-400' : 'text-gray-600'}`}>{task.description}</p>
                <p className="text-xs mt-2 text-gray-400">Criado em: {formatDate(task.createdAt)}</p>
            </div>
            <div className="flex space-x-2 ml-4">
                <button onClick={() => alert(`Ação de edição para a tarefa: ${task.title}`)} className="p-2 text-gray-400 hover:text-violet-700 transition duration-150 rounded-full hover:bg-gray-100" aria-label="Editar Tarefa"><Edit className="w-5 h-5" /></button>
                <button onClick={handleDelete} className="p-2 text-gray-400 hover:text-red-500 transition duration-150 rounded-full hover:bg-red-50" aria-label="Deletar Tarefa" disabled={isDeleting}>{isDeleting ? <Loader2 className="w-5 h-5 animate-spin" /> : <Trash2 className="w-5 h-5" />}</button>
            </div>
        </div>
    );
};

const Header = ({ user, goToHome, goToTasks, onLogout, activePage }) => (
    <header className="flex justify-between items-center bg-white p-4 border-b border-gray-100 shadow-sm rounded-xl">
        <div className="flex items-center space-x-3">
            <ListTodo className="w-6 h-6 text-violet-700" />
            <h1 className="text-xl font-bold text-gray-900">Checklist</h1>
        </div>
        <nav className="flex items-center space-x-6">
            <NavLink icon={Home} label="Home" active={activePage === 'Home'} onClick={goToHome} />
            <NavLink icon={ListTodo} label="Tarefas" active={activePage === 'Tarefas'} onClick={goToTasks} />
        </nav>
        <div className="flex items-center space-x-4">
            <span className="text-gray-600 text-sm hidden sm:inline">Bem-vindo, {user?.displayName || 'Usuário'}</span>
            <Button variant="danger" icon={LogOut} className="py-1 px-3 text-sm border-0" onClick={onLogout}>Sair</Button>
        </div>
    </header>
);

const NavLink = ({ icon: Icon, label, active, onClick }) => (
    <button onClick={onClick} className={`flex items-center p-2 rounded-lg transition-colors duration-150 text-sm font-medium ${active ? 'bg-violet-100 text-violet-700 font-semibold' : 'text-gray-600 hover:bg-gray-50'}`}>
        <Icon className="w-5 h-5 mr-2" />
        {label}
    </button>
);

export default function App() {
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [user, setUser] = useState(null);
    const [currentPage, setCurrentPage] = useState('Login');

    // Ao montar, se já tivermos tokens, tentar recuperar o usuário atual
    useEffect(() => {
        let mounted = true;
        const init = async () => {
            try {
                const me = await api.getMe();
                const userObj = Array.isArray(me) && me.length > 0 ? me[0] : me;
                if (userObj && mounted) {
                    setUser({ displayName: userObj.first_name || (userObj.email || '').split('@')[0], email: userObj.email });
                    setIsLoggedIn(true);
                    setCurrentPage('Home');
                }
            } catch (err) {
                // sem sessão válida
            }
        };
        init();
        return () => { mounted = false; };
    }, []);

    // pass user to useTasks so tasks are scoped per-user
    const { tasks, loading: tasksLoading, error: tasksError, addTask, toggleTask, deleteTask } = useTasks(isLoggedIn, user);

    const goToHome = () => setCurrentPage('Home');
    const goToTasks = () => setCurrentPage('Tasks');
    const goToLogin = () => setCurrentPage('Login');
    const goToRegister = () => setCurrentPage('Register');

    const handleLogin = (userData) => {
        setUser(userData);
        setIsLoggedIn(true);
        goToHome();
    };

    const handleRegister = (userData) => {
        // userData already saved in localStorage by RegistrationPage
        setUser(userData);
        setIsLoggedIn(true);
        goToHome();
    };

    const handleLogout = () => {
        api.logout();
        setUser(null);
        setIsLoggedIn(false);
        // keeping currentPage to Login
        setCurrentPage('Login');
    };

    useEffect(() => {
        if (isLoggedIn && currentPage === 'Login') goToHome();
        if (!isLoggedIn && currentPage !== 'Login') goToLogin();
    }, [isLoggedIn, currentPage]);

    const renderContent = () => {
        if (!isLoggedIn && currentPage === 'Register') {
            return <RegistrationPage onRegister={handleRegister} onSwitchToLogin={goToLogin} />;
        }
        if (!isLoggedIn) {
            return <LoginPage onLogin={handleLogin} onSwitchToRegister={goToRegister} />;
        }

        switch (currentPage) {
            case 'Home':
                return <DashboardPage user={user} tasks={tasks} goToTasks={goToTasks} onLogout={handleLogout} />;
            case 'Tasks':
                return <TasksPage user={user} tasks={tasks} loading={tasksLoading} error={tasksError} addTask={addTask} toggleTask={toggleTask} deleteTask={deleteTask} goToHome={goToHome} onLogout={handleLogout} />;
            default:
                return <p className="text-center mt-20">Página não encontrada.</p>;
        }
    };

    return <div className="min-h-screen bg-gray-50 font-sans">{renderContent()}</div>;
}
