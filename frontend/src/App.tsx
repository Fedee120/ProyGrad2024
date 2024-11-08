import { Route, Routes } from "react-router-dom";
import { AuthProvider } from "./contexts/AuthContext";
import PrivateRoute from "./routes/PrivateRoute";
import Home from "./pages/home/Home";
import Login from "./components/auth/Login";
import { ToastContainer, Slide } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import NotFound from "./components/common/NotFound/NotFound";
import Chat from './components/chat/Chat';

function App() {
  return (
    <div>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<PrivateRoute component={Home} />} />
          <Route path="/login" element={<Login />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
        <ToastContainer
          position="bottom-center"
          autoClose={2500}
          hideProgressBar={false}
          closeOnClick={false}
          pauseOnHover={true}
          draggable={true}
          theme="dark"
          transition={Slide}
        />
        <Chat />
      </AuthProvider>
    </div>
  );
}

export default App;
