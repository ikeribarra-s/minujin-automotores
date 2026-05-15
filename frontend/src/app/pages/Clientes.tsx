import { useState, useEffect } from "react";
import { Phone, MapPin, Search, History } from "lucide-react";
import { toast } from "sonner";
import { api, parseDecimal } from "../api";
import type { Cliente, Venta, Vehiculo, Cobro } from "../api";
import { formatCurrency, formatDate } from "../lib/utils";
import StatusBadge from "../components/StatusBadge";
import Button from "../components/Button";
import Input from "../components/Input";
import Textarea from "../components/Textarea";
import Modal from "../components/Modal";

const emptyCliente = {
  nombre: '',
  apellido: '',
  dni: '',
  telefono: '',
  email: '',
  direccion: '',
};

export default function Clientes() {
  const [activeTab, setActiveTab] = useState<'lista' | 'agregar'>('lista');
  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [editingCliente, setEditingCliente] = useState<Cliente | null>(null);
  const [deletingCliente, setDeletingCliente] = useState<Cliente | null>(null);
  const [historialCliente, setHistorialCliente] = useState<Cliente | null>(null);
  const [historialLoading, setHistorialLoading] = useState(false);
  const [allVentas, setAllVentas] = useState<Venta[]>([]);
  const [allVehiculos, setAllVehiculos] = useState<Vehiculo[]>([]);
  const [allCobros, setAllCobros] = useState<Cobro[]>([]);
  const [historialLoaded, setHistorialLoaded] = useState(false);
  const [nuevoCliente, setNuevoCliente] = useState(emptyCliente);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    api
      .get('/clientes/')
      .then(setClientes)
      .catch((e) => toast.error(e.message))
      .finally(() => setLoading(false));
  }, []);

  const filteredClientes = clientes.filter((cliente) => {
    const q = searchTerm.toLowerCase();
    return (
      cliente.nombre.toLowerCase().includes(q) ||
      cliente.apellido.toLowerCase().includes(q) ||
      (cliente.dni ?? '').includes(searchTerm)
    );
  });

  const handleAgregarCliente = async () => {
    if (!nuevoCliente.nombre || !nuevoCliente.apellido) {
      toast.error('Nombre y apellido son obligatorios');
      return;
    }
    setSaving(true);
    try {
      const created = await api.post('/clientes/', {
        nombre: nuevoCliente.nombre,
        apellido: nuevoCliente.apellido,
        dni: nuevoCliente.dni || undefined,
        telefono: nuevoCliente.telefono || undefined,
        email: nuevoCliente.email || undefined,
        direccion: nuevoCliente.direccion || undefined,
      }) as Cliente;
      setClientes((prev) => [...prev, created].sort((a, b) => a.apellido.localeCompare(b.apellido)));
      setNuevoCliente(emptyCliente);
      setActiveTab('lista');
      toast.success('Cliente agregado');
    } catch (e: any) {
      toast.error(e.message);
    } finally {
      setSaving(false);
    }
  };

  const handleVerHistorial = async (cliente: Cliente) => {
    setHistorialCliente(cliente);
    if (historialLoaded) return;
    setHistorialLoading(true);
    try {
      const [v, veh, c] = await Promise.all([
        api.get('/ventas/'),
        api.get('/vehiculos/'),
        api.get('/cobros/'),
      ]);
      setAllVentas(v);
      setAllVehiculos(veh);
      setAllCobros(c);
      setHistorialLoaded(true);
    } catch (e: any) {
      toast.error(e.message);
    } finally {
      setHistorialLoading(false);
    }
  };

  const handleDeleteCliente = async () => {
    if (!deletingCliente) return;
    setSaving(true);
    try {
      await api.delete(`/clientes/${deletingCliente.id}`);
      setClientes((prev) => prev.filter((c) => c.id !== deletingCliente.id));
      setDeletingCliente(null);
      toast.success('Cliente eliminado');
    } catch (e: any) {
      if (e.message?.includes('409') || e.message?.toLowerCase().includes('tiene ventas') || e.status === 409) {
        toast.error('No se puede eliminar: el cliente tiene ventas asociadas');
      } else {
        toast.error(e.message);
      }
    } finally {
      setSaving(false);
    }
  };

  const handleSaveEdit = async () => {
    if (!editingCliente) return;
    setSaving(true);
    try {
      const updated = await api.put(`/clientes/${editingCliente.id}`, {
        nombre: editingCliente.nombre,
        apellido: editingCliente.apellido,
        dni: editingCliente.dni || undefined,
        telefono: editingCliente.telefono || undefined,
        email: editingCliente.email || undefined,
        direccion: editingCliente.direccion || undefined,
      }) as Cliente;
      setClientes((prev) => prev.map((c) => (c.id === updated.id ? updated : c)));
      setEditingCliente(null);
      toast.success('Cliente actualizado');
    } catch (e: any) {
      toast.error(e.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">Clientes</h1>

      <div className="border-b border-gray-200">
        <div className="flex gap-6">
          {(['lista', 'agregar'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`pb-3 px-1 border-b-2 font-medium capitalize transition-colors ${
                activeTab === tab
                  ? 'border-[#FF6B2B] text-[#FF6B2B]'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              {tab === 'lista' ? 'Lista' : 'Agregar'}
            </button>
          ))}
        </div>
      </div>

      {activeTab === 'lista' && (
        <div className="space-y-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <Input
              placeholder="Buscar por nombre, apellido o DNI"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>

          {loading ? (
            <div className="bg-white rounded-lg border border-gray-200 shadow-sm divide-y divide-gray-200">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="p-4 animate-pulse">
                  <div className="h-4 bg-gray-200 rounded w-1/3 mb-2" />
                  <div className="h-4 bg-gray-200 rounded w-1/4" />
                </div>
              ))}
            </div>
          ) : (
            <div className="bg-white rounded-lg border border-gray-200 shadow-sm divide-y divide-gray-200">
              {filteredClientes.map((cliente) => (
                <div key={cliente.id} className="p-4 hover:bg-gray-50 transition-colors">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-center">
                    <div>
                      <h3 className="font-semibold text-gray-900">
                        {cliente.apellido.toUpperCase()}, {cliente.nombre}
                      </h3>
                      {cliente.dni && <p className="text-sm text-gray-600">DNI {cliente.dni}</p>}
                      {cliente.email && <p className="text-sm text-gray-500">{cliente.email}</p>}
                    </div>
                    <div className="space-y-1">
                      {cliente.telefono && (
                        <div className="flex items-center gap-2 text-sm text-gray-700">
                          <Phone className="w-4 h-4" />
                          {cliente.telefono}
                        </div>
                      )}
                      {cliente.direccion && (
                        <div className="flex items-start gap-2 text-sm text-gray-500">
                          <MapPin className="w-4 h-4 mt-0.5 flex-shrink-0" />
                          {cliente.direccion}
                        </div>
                      )}
                    </div>
                    <div className="flex justify-end gap-2">
                      <Button variant="secondary" onClick={() => handleVerHistorial(cliente)}>
                        <History className="w-4 h-4 mr-1 inline" />
                        Historial
                      </Button>
                      <Button variant="secondary" onClick={() => setEditingCliente(cliente)}>
                        Editar
                      </Button>
                      <Button variant="danger" onClick={() => setDeletingCliente(cliente)}>
                        Eliminar
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
              {filteredClientes.length === 0 && (
                <div className="p-8 text-center text-gray-500">
                  No se encontraron clientes
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {activeTab === 'agregar' && (
        <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <Input label="Nombre" value={nuevoCliente.nombre} onChange={(e) => setNuevoCliente({ ...nuevoCliente, nombre: e.target.value })} required />
            <Input label="Apellido" value={nuevoCliente.apellido} onChange={(e) => setNuevoCliente({ ...nuevoCliente, apellido: e.target.value })} required />
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <Input label="DNI" value={nuevoCliente.dni} onChange={(e) => setNuevoCliente({ ...nuevoCliente, dni: e.target.value })} />
            <Input label="Teléfono" value={nuevoCliente.telefono} onChange={(e) => setNuevoCliente({ ...nuevoCliente, telefono: e.target.value })} />
          </div>
          <Input label="Email" type="email" value={nuevoCliente.email} onChange={(e) => setNuevoCliente({ ...nuevoCliente, email: e.target.value })} className="mb-4" />
          <Textarea label="Dirección" value={nuevoCliente.direccion} onChange={(e) => setNuevoCliente({ ...nuevoCliente, direccion: e.target.value })} className="mb-4" />
          <Button variant="primary" onClick={handleAgregarCliente} className="w-full" disabled={saving}>
            {saving ? 'Guardando...' : 'Guardar'}
          </Button>
        </div>
      )}

      {historialCliente && (() => {
        const ventas = allVentas.filter((v) => v.cliente_id === historialCliente.id);
        const totalVentas = ventas.reduce((s, v) => s + parseDecimal(v.precio_final), 0);
        const totalCobrado = allCobros
          .filter((c) => ventas.some((v) => v.id === c.venta_id))
          .reduce((s, c) => s + parseDecimal(c.monto), 0);
        return (
          <Modal isOpen={true} onClose={() => setHistorialCliente(null)} title={`Historial — ${historialCliente.apellido.toUpperCase()}, ${historialCliente.nombre}`}>
            <div className="space-y-4">
              {historialLoading ? (
                <div className="space-y-3">
                  {[...Array(2)].map((_, i) => (
                    <div key={i} className="h-20 bg-gray-100 rounded-lg animate-pulse" />
                  ))}
                </div>
              ) : ventas.length === 0 ? (
                <p className="text-gray-500 text-sm py-6 text-center">Sin ventas registradas</p>
              ) : (
                <div className="space-y-3">
                  {[...ventas]
                    .sort((a, b) => new Date(b.fecha_venta).getTime() - new Date(a.fecha_venta).getTime())
                    .map((venta) => {
                      const vehiculo = allVehiculos.find((v) => v.id === venta.vehiculo_id);
                      const cobros = allCobros.filter((c) => c.venta_id === venta.id);
                      const cobrado = cobros.reduce((s, c) => s + parseDecimal(c.monto), 0);
                      const saldo = parseDecimal(venta.precio_final) - cobrado;
                      return (
                        <div key={venta.id} className="border border-gray-200 rounded-lg overflow-hidden">
                          <div className="bg-gray-50 px-4 py-3 flex items-center justify-between">
                            <div>
                              <p className="font-semibold text-gray-900">
                                {vehiculo ? `${vehiculo.marca} ${vehiculo.modelo} ${vehiculo.anio}` : `Vehículo #${venta.vehiculo_id}`}
                              </p>
                              <p className="text-xs text-gray-500">{formatDate(venta.fecha_venta)} · <span className="capitalize">{venta.forma_pago}</span></p>
                            </div>
                            <div className="text-right">
                              <p className="font-bold text-gray-900">{formatCurrency(parseDecimal(venta.precio_final))}</p>
                              <StatusBadge status={saldo > 0.01 ? 'pendiente' : 'cobrado'} className="mt-1" />
                            </div>
                          </div>
                          {cobros.length > 0 && (
                            <div className="divide-y divide-gray-100">
                              {cobros.map((cobro) => (
                                <div key={cobro.id} className="px-4 py-2 flex items-center justify-between text-sm">
                                  <span className="text-gray-600 capitalize">{cobro.concepto} · {cobro.forma_pago} · {formatDate(cobro.fecha)}</span>
                                  <span className="font-medium text-green-700">{formatCurrency(parseDecimal(cobro.monto))}</span>
                                </div>
                              ))}
                              <div className="px-4 py-2 flex justify-between text-sm font-semibold bg-gray-50">
                                <span className={saldo > 0.01 ? 'text-red-600' : 'text-green-600'}>
                                  {saldo > 0.01 ? `Saldo: ${formatCurrency(saldo)}` : 'Pagado'}
                                </span>
                                <span className="text-gray-700">Cobrado: {formatCurrency(cobrado)}</span>
                              </div>
                            </div>
                          )}
                        </div>
                      );
                    })}
                </div>
              )}
              {ventas.length > 0 && (
                <div className="border-t pt-3 grid grid-cols-3 gap-2 text-sm text-center">
                  <div>
                    <p className="text-gray-500">Ventas</p>
                    <p className="font-bold text-gray-900">{ventas.length}</p>
                  </div>
                  <div>
                    <p className="text-gray-500">Total facturado</p>
                    <p className="font-bold text-gray-900">{formatCurrency(totalVentas)}</p>
                  </div>
                  <div>
                    <p className="text-gray-500">Total cobrado</p>
                    <p className="font-bold text-green-700">{formatCurrency(totalCobrado)}</p>
                  </div>
                </div>
              )}
              <Button variant="secondary" onClick={() => setHistorialCliente(null)} className="w-full">
                Cerrar
              </Button>
            </div>
          </Modal>
        );
      })()}

      {deletingCliente && (
        <Modal isOpen={true} onClose={() => setDeletingCliente(null)} title="¿Eliminar cliente?" className="max-w-md">
          <div className="space-y-4">
            <p className="text-gray-700">
              ¿Eliminar a <strong>{deletingCliente.apellido.toUpperCase()}, {deletingCliente.nombre}</strong>?
            </p>
            <div className="bg-amber-50 border border-amber-200 rounded-lg p-3">
              <p className="text-sm text-amber-800">Esta acción no se puede deshacer. Fallará si el cliente tiene ventas asociadas.</p>
            </div>
            <div className="flex gap-3">
              <Button variant="danger" onClick={handleDeleteCliente} className="flex-1" disabled={saving}>
                {saving ? 'Eliminando...' : 'Sí, eliminar'}
              </Button>
              <Button variant="secondary" onClick={() => setDeletingCliente(null)} className="flex-1">
                Cancelar
              </Button>
            </div>
          </div>
        </Modal>
      )}

      {editingCliente && (
        <Modal isOpen={true} onClose={() => setEditingCliente(null)} title="Editar cliente">
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input label="Nombre" value={editingCliente.nombre} onChange={(e) => setEditingCliente({ ...editingCliente, nombre: e.target.value })} required />
              <Input label="Apellido" value={editingCliente.apellido} onChange={(e) => setEditingCliente({ ...editingCliente, apellido: e.target.value })} required />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input label="DNI" value={editingCliente.dni ?? ''} onChange={(e) => setEditingCliente({ ...editingCliente, dni: e.target.value || null })} />
              <Input label="Teléfono" value={editingCliente.telefono ?? ''} onChange={(e) => setEditingCliente({ ...editingCliente, telefono: e.target.value || null })} />
            </div>
            <Input label="Email" type="email" value={editingCliente.email ?? ''} onChange={(e) => setEditingCliente({ ...editingCliente, email: e.target.value || null })} />
            <Textarea label="Dirección" value={editingCliente.direccion ?? ''} onChange={(e) => setEditingCliente({ ...editingCliente, direccion: e.target.value || null })} />
            <div className="flex gap-3 pt-4">
              <Button variant="primary" onClick={handleSaveEdit} className="flex-1" disabled={saving}>
                {saving ? 'Guardando...' : 'Guardar cambios'}
              </Button>
              <Button variant="secondary" onClick={() => setEditingCliente(null)} className="flex-1">
                Cancelar
              </Button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
}
