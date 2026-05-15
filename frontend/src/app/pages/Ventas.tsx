import { useState, useEffect } from "react";
import { toast } from "sonner";
import { api, parseDecimal } from "../api";
import type { Venta, Vehiculo, Cliente, Cobro } from "../api";
import { formatCurrency, formatDate } from "../lib/utils";
import StatusBadge from "../components/StatusBadge";
import Button from "../components/Button";
import Input from "../components/Input";
import Select from "../components/Select";
import Textarea from "../components/Textarea";
import Modal from "../components/Modal";

export default function Ventas() {
  const [activeTab, setActiveTab] = useState<'lista' | 'registrar'>('lista');
  const [ventas, setVentas] = useState<Venta[]>([]);
  const [vehiculos, setVehiculos] = useState<Vehiculo[]>([]);
  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [cobros, setCobros] = useState<Cobro[]>([]);
  const [loading, setLoading] = useState(true);
  const [editingVenta, setEditingVenta] = useState<Venta | null>(null);
  const [cobrosVenta, setCobrosVenta] = useState<Venta | null>(null);
  const [saving, setSaving] = useState(false);

  const [nuevaVenta, setNuevaVenta] = useState({
    vehiculo_id: 0,
    cliente_id: 0,
    precio_final: '',
    forma_pago: 'contado' as Venta['forma_pago'],
    observaciones: '',
  });

  useEffect(() => {
    Promise.all([
      api.get('/ventas/'),
      api.get('/vehiculos/'),
      api.get('/clientes/'),
      api.get('/cobros/'),
    ])
      .then(([v, veh, c, co]) => {
        setVentas(v);
        setVehiculos(veh);
        setClientes(c);
        setCobros(co);
      })
      .catch((e) => toast.error(e.message))
      .finally(() => setLoading(false));
  }, []);

  const vehiculosDisponibles = vehiculos.filter((v) => v.estado === 'disponible');

  const getVehiculo = (id: number) => vehiculos.find((v) => v.id === id);
  const getCliente = (id: number) => clientes.find((c) => c.id === id);

  const handleRegistrarVenta = async () => {
    if (!nuevaVenta.vehiculo_id || !nuevaVenta.cliente_id || !nuevaVenta.precio_final) {
      toast.error('Vehículo, cliente y precio son obligatorios');
      return;
    }
    setSaving(true);
    try {
      const created = await api.post('/ventas/', {
        vehiculo_id: nuevaVenta.vehiculo_id,
        cliente_id: nuevaVenta.cliente_id,
        precio_final: parseFloat(nuevaVenta.precio_final),
        forma_pago: nuevaVenta.forma_pago,
        observaciones: nuevaVenta.observaciones || undefined,
      }) as Venta;
      setVentas((prev) => [created, ...prev]);
      // Mark vehicle as sold in local state
      setVehiculos((prev) =>
        prev.map((v) => (v.id === nuevaVenta.vehiculo_id ? { ...v, estado: 'vendido' as const } : v))
      );
      setNuevaVenta({ vehiculo_id: 0, cliente_id: 0, precio_final: '', forma_pago: 'contado', observaciones: '' });
      setActiveTab('lista');
      toast.success('Venta registrada');
    } catch (e: any) {
      toast.error(e.message);
    } finally {
      setSaving(false);
    }
  };

  const handleSaveEdit = async () => {
    if (!editingVenta) return;
    setSaving(true);
    try {
      const updated = await api.put(`/ventas/${editingVenta.id}`, {
        precio_final: parseDecimal(editingVenta.precio_final),
        forma_pago: editingVenta.forma_pago,
        observaciones: editingVenta.observaciones || undefined,
      }) as Venta;
      setVentas((prev) => prev.map((v) => (v.id === updated.id ? updated : v)));
      setEditingVenta(null);
      toast.success('Venta actualizada');
    } catch (e: any) {
      toast.error(e.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">Ventas</h1>

      <div className="border-b border-gray-200">
        <div className="flex gap-6">
          {(['lista', 'registrar'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`pb-3 px-1 border-b-2 font-medium transition-colors ${
                activeTab === tab
                  ? 'border-[#FF6B2B] text-[#FF6B2B]'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              {tab === 'lista' ? 'Lista' : 'Registrar'}
            </button>
          ))}
        </div>
      </div>

      {activeTab === 'lista' && (
        loading ? (
          <div className="bg-white rounded-lg border border-gray-200 shadow-sm divide-y divide-gray-200">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="p-4 animate-pulse">
                <div className="h-4 bg-gray-200 rounded w-1/3 mb-2" />
                <div className="h-4 bg-gray-200 rounded w-1/4" />
              </div>
            ))}
          </div>
        ) : (
          <div className="bg-white rounded-lg border border-gray-200 shadow-sm divide-y divide-gray-200">
            {[...ventas]
              .sort((a, b) => new Date(b.fecha_venta).getTime() - new Date(a.fecha_venta).getTime())
              .map((venta) => {
                const vehiculo = getVehiculo(venta.vehiculo_id);
                const cliente = getCliente(venta.cliente_id);
                const ventaCobros = cobros.filter((c) => c.venta_id === venta.id);
                const totalCobrado = ventaCobros.reduce((sum, c) => sum + parseDecimal(c.monto), 0);
                const saldo = parseDecimal(venta.precio_final) - totalCobrado;
                return (
                  <div key={venta.id} className="p-4 hover:bg-gray-50 transition-colors">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-center">
                      <div>
                        <h3 className="font-semibold text-gray-900">
                          {cliente ? `${cliente.apellido.toUpperCase()}, ${cliente.nombre}` : `Cliente #${venta.cliente_id}`}
                        </h3>
                        <p className="text-sm text-gray-600">
                          {vehiculo ? `${vehiculo.marca} ${vehiculo.modelo} ${vehiculo.anio}` : `Vehículo #${venta.vehiculo_id}`}
                        </p>
                        <p className="text-sm text-gray-500">{formatDate(venta.fecha_venta)}</p>
                        {venta.observaciones && (
                          <p className="text-sm text-gray-400 mt-1">{venta.observaciones}</p>
                        )}
                      </div>
                      <div>
                        <p className="text-2xl font-bold text-gray-900">
                          {formatCurrency(parseDecimal(venta.precio_final))}
                        </p>
                        <StatusBadge status={venta.forma_pago} className="mt-2" />
                        {ventaCobros.length > 0 && (
                          <div className="mt-2 text-xs text-gray-500 space-y-0.5">
                            <p>Cobrado: <span className="text-green-700 font-medium">{formatCurrency(totalCobrado)}</span></p>
                            {saldo > 0.01 && <p>Saldo: <span className="text-red-600 font-medium">{formatCurrency(saldo)}</span></p>}
                            {saldo <= 0.01 && <p className="text-green-600 font-medium">Pagado</p>}
                          </div>
                        )}
                      </div>
                      <div className="flex justify-end gap-2">
                        <Button variant="secondary" onClick={() => setCobrosVenta(venta)}>
                          Cobros {ventaCobros.length > 0 && `(${ventaCobros.length})`}
                        </Button>
                        <Button variant="secondary" onClick={() => setEditingVenta(venta)}>
                          Editar
                        </Button>
                      </div>
                    </div>
                  </div>
                );
              })}
            {ventas.length === 0 && (
              <div className="p-8 text-center text-gray-500">No hay ventas registradas</div>
            )}
          </div>
        )
      )}

      {activeTab === 'registrar' && (
        <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
          <Select
            label="Vehículo"
            options={[
              { value: '0', label: 'Seleccione un vehículo' },
              ...vehiculosDisponibles.map((v) => ({
                value: v.id.toString(),
                label: `${v.marca} ${v.modelo} ${v.anio} — ${v.patente ?? 'Sin patente'}`,
              })),
            ]}
            value={nuevaVenta.vehiculo_id.toString()}
            onChange={(e) => setNuevaVenta({ ...nuevaVenta, vehiculo_id: parseInt(e.target.value) })}
            className="mb-4"
            required
          />
          <Select
            label="Cliente"
            options={[
              { value: '0', label: 'Seleccione un cliente' },
              ...clientes.map((c) => ({
                value: c.id.toString(),
                label: `${c.apellido}, ${c.nombre}${c.dni ? ` — DNI ${c.dni}` : ''}`,
              })),
            ]}
            value={nuevaVenta.cliente_id.toString()}
            onChange={(e) => setNuevaVenta({ ...nuevaVenta, cliente_id: parseInt(e.target.value) })}
            className="mb-4"
            required
          />
          <Input
            label="Precio final"
            type="number"
            value={nuevaVenta.precio_final}
            onChange={(e) => setNuevaVenta({ ...nuevaVenta, precio_final: e.target.value })}
            className="mb-4"
            required
          />
          <Select
            label="Forma de pago"
            options={[
              { value: 'contado', label: 'Contado' },
              { value: 'financiado', label: 'Financiado' },
              { value: 'permuta', label: 'Permuta' },
              { value: 'mixto', label: 'Mixto' },
            ]}
            value={nuevaVenta.forma_pago}
            onChange={(e) => setNuevaVenta({ ...nuevaVenta, forma_pago: e.target.value as Venta['forma_pago'] })}
            className="mb-4"
          />
          <Textarea
            label="Observaciones"
            value={nuevaVenta.observaciones}
            onChange={(e) => setNuevaVenta({ ...nuevaVenta, observaciones: e.target.value })}
            className="mb-4"
          />
          <Button variant="primary" onClick={handleRegistrarVenta} className="w-full" disabled={saving}>
            {saving ? 'Registrando...' : 'Registrar venta'}
          </Button>
        </div>
      )}

      {cobrosVenta && (() => {
        const ventaCobros = cobros.filter((c) => c.venta_id === cobrosVenta.id);
        const totalCobrado = ventaCobros.reduce((sum, c) => sum + parseDecimal(c.monto), 0);
        const saldo = parseDecimal(cobrosVenta.precio_final) - totalCobrado;
        const vehiculo = getVehiculo(cobrosVenta.vehiculo_id);
        const cliente = getCliente(cobrosVenta.cliente_id);
        return (
          <Modal isOpen={true} onClose={() => setCobrosVenta(null)} title="Cobros de la venta">
            <div className="space-y-4">
              <div className="bg-gray-50 rounded-lg p-3 text-sm text-gray-700">
                {vehiculo ? `${vehiculo.marca} ${vehiculo.modelo} ${vehiculo.anio}` : `Vehículo #${cobrosVenta.vehiculo_id}`}
                {' · '}
                {cliente ? `${cliente.apellido}, ${cliente.nombre}` : `Cliente #${cobrosVenta.cliente_id}`}
                {' · '}
                {formatCurrency(parseDecimal(cobrosVenta.precio_final))}
              </div>
              {ventaCobros.length === 0 ? (
                <p className="text-gray-500 text-sm py-4 text-center">No hay cobros registrados para esta venta</p>
              ) : (
                <div className="divide-y divide-gray-100 border border-gray-200 rounded-lg overflow-hidden">
                  {ventaCobros.map((cobro) => (
                    <div key={cobro.id} className="flex items-center justify-between p-3 text-sm">
                      <div>
                        <p className="font-medium text-gray-900">{formatCurrency(parseDecimal(cobro.monto))}</p>
                        <p className="text-gray-500">{formatDate(cobro.fecha)} · {cobro.concepto} · {cobro.forma_pago}</p>
                        {cobro.observaciones && <p className="text-gray-400">{cobro.observaciones}</p>}
                      </div>
                      <StatusBadge status={cobro.concepto} />
                    </div>
                  ))}
                </div>
              )}
              <div className="border-t pt-3 space-y-1 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Precio venta</span>
                  <span className="font-medium">{formatCurrency(parseDecimal(cobrosVenta.precio_final))}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Total cobrado</span>
                  <span className="font-medium text-green-700">{formatCurrency(totalCobrado)}</span>
                </div>
                <div className="flex justify-between font-semibold">
                  <span>Saldo pendiente</span>
                  <span className={saldo > 0.01 ? 'text-red-600' : 'text-green-600'}>
                    {saldo > 0.01 ? formatCurrency(saldo) : 'Pagado'}
                  </span>
                </div>
              </div>
              <Button variant="secondary" onClick={() => setCobrosVenta(null)} className="w-full">
                Cerrar
              </Button>
            </div>
          </Modal>
        );
      })()}

      {editingVenta && (
        <Modal isOpen={true} onClose={() => setEditingVenta(null)} title="Editar venta">
          <div className="space-y-4">
            <div className="bg-gray-50 rounded-lg p-3 text-sm text-gray-700">
              {(() => {
                const v = getVehiculo(editingVenta.vehiculo_id);
                const c = getCliente(editingVenta.cliente_id);
                return `${v ? `${v.marca} ${v.modelo}` : `Vehículo #${editingVenta.vehiculo_id}`} · ${c ? `${c.apellido}, ${c.nombre}` : `Cliente #${editingVenta.cliente_id}`} · ${formatDate(editingVenta.fecha_venta)}`;
              })()}
            </div>
            <Input
              label="Precio final"
              type="number"
              value={editingVenta.precio_final}
              onChange={(e) => setEditingVenta({ ...editingVenta, precio_final: e.target.value })}
            />
            <Select
              label="Forma de pago"
              options={[
                { value: 'contado', label: 'Contado' },
                { value: 'financiado', label: 'Financiado' },
                { value: 'permuta', label: 'Permuta' },
                { value: 'mixto', label: 'Mixto' },
              ]}
              value={editingVenta.forma_pago}
              onChange={(e) => setEditingVenta({ ...editingVenta, forma_pago: e.target.value as Venta['forma_pago'] })}
            />
            <Textarea
              label="Observaciones"
              value={editingVenta.observaciones ?? ''}
              onChange={(e) => setEditingVenta({ ...editingVenta, observaciones: e.target.value || null })}
            />
            <div className="flex gap-3 pt-4">
              <Button variant="primary" onClick={handleSaveEdit} className="flex-1" disabled={saving}>
                {saving ? 'Guardando...' : 'Guardar cambios'}
              </Button>
              <Button variant="secondary" onClick={() => setEditingVenta(null)} className="flex-1">
                Cancelar
              </Button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
}
