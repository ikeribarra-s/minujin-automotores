import { createBrowserRouter } from "react-router";
import Layout from "./components/Layout";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Stock from "./pages/Stock";
import Clientes from "./pages/Clientes";
import Ventas from "./pages/Ventas";
import Cobros from "./pages/Cobros";
import Cheques from "./pages/Cheques";

export const router = createBrowserRouter([
  {
    path: "/login",
    Component: Login,
  },
  {
    path: "/",
    Component: Layout,
    children: [
      { index: true, Component: Dashboard },
      { path: "stock", Component: Stock },
      { path: "clientes", Component: Clientes },
      { path: "ventas", Component: Ventas },
      { path: "cobros", Component: Cobros },
      { path: "cheques", Component: Cheques },
    ],
  },
]);
