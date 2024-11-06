import React, { useState, useEffect } from 'react';
import { Bell, LogOut, User, PieChart, Activity } from 'lucide-react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

const Dashboard = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [activeTab, setActiveTab] = useState('symptoms');
  const [symptoms, setSymptoms] = useState([]);
  const [user, setUser] = useState(null);
  const [loginForm, setLoginForm] = useState({ username: '', password: '' });
  const [registerForm, setRegisterForm] = useState({
    username: '',
    password: '',
    age: '',
    gender: '',
    location: ''
  });

  const fetchSymptoms = async (userId) => {
    try {
      const response = await fetch(`/users/${userId}/symptoms`);
      const data = await response.json();
      setSymptoms(data);
    } catch (error) {
      console.error('Error fetching symptoms:', error);
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    // TODO: Implement login API endpoint
    // For now, just simulate login with test user
    setUser({ id: 1, username: loginForm.username });
    setIsLoggedIn(true);
    fetchSymptoms(1);
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('/create_user', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(registerForm),
      });
      if (response.ok) {
        setActiveTab('login');
      }
    } catch (error) {
      console.error('Error registering:', error);
    }
  };

  const handleAddSymptom = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`/users/${user.id}/symptoms`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          label: e.target.label.value,
          description: e.target.description.value,
        }),
      });
      if (response.ok) {
        fetchSymptoms(user.id);
        e.target.reset();
      }
    } catch (error) {
      console.error('Error adding symptom:', error);
    }
  };

  if (!isLoggedIn) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <Card className="w-96">
          <CardHeader>
            <CardTitle>{activeTab === 'login' ? 'Login' : 'Register'}</CardTitle>
            <CardDescription>
              {activeTab === 'login' 
                ? 'Enter your credentials to access your dashboard' 
                : 'Create a new account'}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {activeTab === 'login' ? (
              <form onSubmit={handleLogin} className="space-y-4">
                <input
                  type="text"
                  placeholder="Username"
                  className="w-full p-2 border rounded"
                  value={loginForm.username}
                  onChange={(e) => setLoginForm({...loginForm, username: e.target.value})}
                />
                <input
                  type="password"
                  placeholder="Password"
                  className="w-full p-2 border rounded"
                  value={loginForm.password}
                  onChange={(e) => setLoginForm({...loginForm, password: e.target.value})}
                />
                <button
                  type="submit"
                  className="w-full bg-blue-500 text-white p-2 rounded hover:bg-blue-600"
                >
                  Login
                </button>
              </form>
            ) : (
              <form onSubmit={handleRegister} className="space-y-4">
                <input
                  type="text"
                  placeholder="Username"
                  className="w-full p-2 border rounded"
                  value={registerForm.username}
                  onChange={(e) => setRegisterForm({...registerForm, username: e.target.value})}
                />
                <input
                  type="password"
                  placeholder="Password"
                  className="w-full p-2 border rounded"
                  value={registerForm.password}
                  onChange={(e) => setRegisterForm({...registerForm, password: e.target.value})}
                />
                <input
                  type="number"
                  placeholder="Age"
                  className="w-full p-2 border rounded"
                  value={registerForm.age}
                  onChange={(e) => setRegisterForm({...registerForm, age: e.target.value})}
                />
                <select
                  className="w-full p-2 border rounded"
                  value={registerForm.gender}
                  onChange={(e) => setRegisterForm({...registerForm, gender: e.target.value})}
                >
                  <option value="">Select Gender</option>
                  <option value="M">Male</option>
                  <option value="F">Female</option>
                  <option value="O">Other</option>
                </select>
                <input
                  type="text"
                  placeholder="Location"
                  className="w-full p-2 border rounded"
                  value={registerForm.location}
                  onChange={(e) => setRegisterForm({...registerForm, location: e.target.value})}
                />
                <button
                  type="submit"
                  className="w-full bg-blue-500 text-white p-2 rounded hover:bg-blue-600"
                >
                  Register
                </button>
              </form>
            )}
            <button
              onClick={() => setActiveTab(activeTab === 'login' ? 'register' : 'login')}
              className="w-full mt-4 text-blue-500 hover:text-blue-600"
            >
              {activeTab === 'login' ? 'Need an account? Register' : 'Already have an account? Login'}
            </button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold">Symptom Tracker</h1>
            </div>
            <div className="flex items-center space-x-4">
              <Bell className="w-6 h-6 text-gray-500" />
              <User className="w-6 h-6 text-gray-500" />
              <span className="font-medium">{user?.username}</span>
              <button
                onClick={() => setIsLoggedIn(false)}
                className="flex items-center text-gray-500 hover:text-gray-700"
              >
                <LogOut className="w-6 h-6" />
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
          {/* Add Symptom Card */}
          <Card>
            <CardHeader>
              <CardTitle>Add New Symptom</CardTitle>
              <CardDescription>Record a new symptom you're experiencing</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleAddSymptom} className="space-y-4">
                <input
                  type="text"
                  name="label"
                  placeholder="Symptom Label"
                  className="w-full p-2 border rounded"
                  required
                />
                <textarea
                  name="description"
                  placeholder="Symptom Description"
                  className="w-full p-2 border rounded"
                  required
                />
                <button
                  type="submit"
                  className="w-full bg-blue-500 text-white p-2 rounded hover:bg-blue-600"
                >
                  Add Symptom
                </button>
              </form>
            </CardContent>
          </Card>

          {/* Symptoms List Card */}
          <Card>
            <CardHeader>
              <CardTitle>Your Symptoms</CardTitle>
              <CardDescription>Recent symptoms you've recorded</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {symptoms.map((symptom) => (
                  <div
                    key={symptom.id}
                    className="p-4 border rounded-lg bg-gray-50"
                  >
                    <h3 className="font-medium">{symptom.label}</h3>
                    <p className="text-gray-600">{symptom.description}</p>
                    <p className="text-sm text-gray-500 mt-2">
                      {new Date(symptom.timestamp).toLocaleString()}
                    </p>
                  </div>
                ))}
                {symptoms.length === 0 && (
                  <p className="text-gray-500 text-center">No symptoms recorded yet</p>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Placeholder cards for future features */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <PieChart className="w-6 h-6" />
                Segmentation Analysis
              </CardTitle>
              <CardDescription>Coming soon - User segmentation insights</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-48 flex items-center justify-center bg-gray-100 rounded-lg">
                <p className="text-gray-500">Feature in development</p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="w-6 h-6" />
                Feature Extraction
              </CardTitle>
              <CardDescription>Coming soon - Symptom pattern analysis</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-48 flex items-center justify-center bg-gray-100 rounded-lg">
                <p className="text-gray-500">Feature in development</p>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;