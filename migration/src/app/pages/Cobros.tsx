import { useState, useEffect } from "react";
import { DollarSign, Building2, FileText, CreditCard } from "lucide-react";
import { toast } from "sonner";
import { api, parseDecimal } from "../api";
import type { Cobro, Venta, Cliente } from "../api";
import { formatCurrency, formatDate } from "../lib/utils";
import StatusBadge from "../components/StatusBadge";
import Button from "../components/Button";
import Input from "../components/Input";
import Select from "../components/Select";
import Textarea from "../components/Textarea";
import Modal from "../components/Modal";

const formaPagoIcons = {
  efectivo: DollarSign,
  transferencia: Building2,
  cheque: FileText,
  tarjeta: CreditCard,
};

export default function Cobros() {
  const [activeTab, setActiveTab] = useState<'lista' | 'registrar'>('lista');
  const [cobros, setCobros] = useState<Cobro[]>([]);
  const [ventas, setVentas] = useState<Venta[]>([]);
  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterVenta, setFilterVenta] = useState<string>('todos');
  const [editingCobro, setEditingCobro] = useState<Cobro | null>(null);
  const [saving, setSaving] = useState(false);

  const [nuevoCobro, setNuevoCobro] = useState({
    venta_id: 0,
    cliente_id: 0,
    monto: '',
    concepto: 'saldo' as Cobro['concepto'],
    forma_pago: 'efectivo' as Cobro['forma_pago'],
    observaciones: '',
  });

  useEffect(() => {
    Promise.all([
      api.get('/cobros/'),
      api.get('/ventas/'),
      api.get('/clientes/'),
    ])
      .then(([c, v, cl]) => {
        setCobros(c);
        setVentas(v);
        setClientes(cl);
      })
      .catch((e) => toast.error(e.message))
      .finally(() => setLoading(false));
  }, []);

  const filteredCobros = cobros.filter((cobro) =>
    filterVenta === 'todos' ? true : cobro.venta_id === parseInt(filterVenta)
  );

  const getCliente = (id: number) => clientes.find((c) => c.id === id);
  const getVenta = (id: number) => ventas.find((v) => v.id === id);

  const handleRegistrarCobro = async () => {
    if (!nuevoCobro.venta_id || !nuevoCobro.monto) {
      toast.error('Venta y monto son obligatorios');
      return;
    }
    setSaving(true);
    try {
      const created = await api.post('/cobros/', {
        venta_id: nuevoCobro.venta_id,
        cliente_id: nuevoCobro.cliente_id,
        monto: parseFloat(nuevoCobro.monto),
        concepto: nuevoCobro.concepto,
        forma_pago: nuevoCobro.forma_pago,
        observaciones: nuevoCobro.observaciones || undefined,
      }) as Cobro;
      setCobros((prev) => [created, ...prev]);
      setNuevoCobro({ venta_id: 0, cliente_id: 0, monto: '', concepto: 'saldo', forma_pago: 'efectivo', observaciones: '' });
      setActiveTab('lista');
      toast.success('Cobro registrado');
    } catch (e: any) {
      toast.error(e.message);
    } finally {
      setSaving(false);
    }
  };

  const handleSaveEdit = async () => {
    if (!editingCobro) return;
    setSaving(true);
    try {
      const updated = await api.patch(`/cobros/${editingCobro.id}`, {
        monto: parseDecimal(editingCobro.monto),
        concepto: editingCobro.concepto,
        forma_pago: editingCobro.forma_pago,
        observaciones: editingCobro.observaciones || undefined,
      }) as Cobro;
      setCobros((prev) => prev.map((c) => (c.id === updated.id ? updated : c)));
      setEditingCobro(null);
      toast.success('Cobro actualizado');
    } catch (e: any) {
      toast.error(e.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">Cobros</h1>

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
        <div className="space-y-4">
          <Select
            options={[
              { value: 'todos', label: 'Todos' },
              ...ventas.map((v) => ({
                value: v.id.toString(),
                label: `Venta #${v.id}`,
              })),
            ]}
            value={filterVenta}
            onChange={(e) => setFilterVenta(e.target.value)}
            className="max-w-xs"
          />

          {loading ? (
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
              {filteredCobros.map((cobro) => {
                const cliente = getCliente(cobro.cliente_id);
                const Icon = formaPagoIcons[cobro.forma_pago];
                return (
                  <div key={cobro.id} className="p-4 hover:bg-gray-50 transition-colors">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-center">
                      <div>
                        <h3 className="font-semibold text-gray-900">
                          {cliente ? `${cliente.apellido.toUpperCase()}, ${cliente.nombre}` : `Cliente #${cobro.cliente_id}`}
                        </h3>
                        <p className="text-sm text-gray-600">Venta #{cobro.venta_id}</p>
                        <p className="text-sm text-gray-500">{formatDate(cobro.fecha)}</p>
                        {cobro.observaciones && (
                          <p className="text-sm text-gray-400 mt-1">{cobro.observaciones}</p>
                        )}
                      </div>
                      <div>
                        <p className="text-2xl font-bold text-gray-900">
                          {formatCurrency(parseDecimal(cobro.monto))}
                        </p>
                        <div className="flex items-center gap-2 mt-1">
                          <Icon className="w-4 h-4 text-gray-400" />
                          <span className="text-sm text-gray-500 capitalize">{cobro.forma_pago}</span>
                        </div>
                        <StatusBadge status={cobro.concepto} className="mt-2" />
                      </div>
                      <div className="flex justify-end">
                        <Button variant="secondary" onClick={() => setEditingCobro(cobro)}>
                          Editar
                        </Button>
                      </div>
                    </div>
                  </div>
                );
              })}
              {filteredCobros.length === 0 && (
                <div className="p-8 text-center text-gray-500">No hay cobros registrados</div>
              )}
            </div>
          )}
        </div>
      )}

      {activeTab === 'registrar' && (
        <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
          <Select
            label="Venta"
            options={[
              { value: '0', label: 'Seleccione una venta' },
              ...ventas.map((v) => {
                const c = getCliente(v.cliente_id);
                return {
                  value: v.id.toString(),
                  label: `Venta #${v.id} — ${c ? `${c.apellido}, ${c.nombre}` : `Cliente #${v.cliente_id}`} — ${formatCurrency(parseDecimal(v.precio_final))}`,
                };
              }),
            ]}
            value={nuevoCobro.venta_id.toString()}
            onChange={(e) => {
              const ventaId = parseInt(e.target.value);
              const venta = getVenta(ventaId);
              setNuevoCobro({ ...nuevoCobro, venta_id: ventaId, cliente_id: venta?.cliente_id ?? 0 });
            }}
            className="mb-4"
            required
          />
          <Select
            label="Cliente"
            options={[
              { value: '0', label: 'Seleccione un cliente' },
              ...clientes.map((c) => ({
                value: c.id.toString(),
                label: `${c.apellido}, ${c.nombre}`,
              })),
            ]}
            value={nuevoCobro.cliente_id.toString()}
            onChange={(e) => setNuevoCobro({ ...nuevoCobro, cliente_id: parseInt(e.target.value) })}
            className="mb-4"
            required
          />
          <Input
            label="Monto"
            type="number"
            value={nuevoCobro.monto}
            onChange={(e) => setNuevoCobro({ ...nuevoCobro, monto: e.target.value })}
            className="mb-4"
            required
          />
          <Select
            label="Concepto"
            options={[
              { value: 'saldo', label: 'Saldo' },
              { value: 'sena', label: 'Seña' },
              { value: 'cuota', label: 'Cuota' },
              { value: 'otro', label: 'Otro' },
            ]}
            value={nuevoCobro.concepto}
            onChange={(e) => setNuevoCobro({ ...nuevoCobro, concepto: e.target.value as Cobro['concepto'] })}
            className="mb-4"
          />
          <Select
            label="Forma de pago"
            options={[
              { value: 'efectivo', label: 'Efectivo' },
              { value: 'transferencia', label: 'Transferencia' },
              { value: 'cheque', label: 'Cheque' },
              { value: 'tarjeta', label: 'Tarjeta' },
            ]}
            value={nuevoCobro.forma_pago}
            onChange={(e) => setNuevoCobro({ ...nuevoCobro, forma_pago: e.target.value as Cobro['forma_pago'] })}
            className="mb-4"
          />
          <Textarea
            label="Observaciones"
            value={nuevoCobro.observaciones}
            onChange={(e) => setNuevoCobro({ ...nuevoCobro, observaciones: e.target.value })}
            className="mb-4"
          />
          <Button variant="primary" onClick={handleRegistrarCobro} className="w-full" disabled={saving}>
            {saving ? 'Registrando...' : 'Registrar cobro'}
          </Button>
        </div>
      )}

      {editingCobro && (
        <Modal isOpen={true} onClose={() => setEditingCobro(null)} title="Editar cobro">
          <div className="space-y-4">
            <div className="bg-gray-50 rounded-lg p-3 text-sm text-gray-700">
              Venta y cliente no son editables
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input
                label="Monto"
                type="number"
                value={editingCobro.monto}
                onChange={(e) => setEditingCobro({ ...editingCobro, monto: e.target.value })}
              />
              <Select
                label="Concepto"
                options={[
                  { value: 'saldo', label: 'Saldo' },
                  { value: 'sena', label: 'Seña' },
                  { value: 'cuota', label: 'Cuota' },
                  { value: 'otro', label: 'Otro' },
                ]}
                value={editingCobro.concepto}
                onChange={(e) => setEditingCobro({ ...editingCobro, concepto: e.target.value as Cobro['concepto'] })}
              />
            </div>
            <Select
              label="Forma de pago"
              options={[
                { value: 'efectivo', label: 'Efectivo' },
                { value: 'transferencia', label: 'Transferencia' },
                { value: 'cheque', label: 'Cheque' },
                { value: 'tarjeta', label: 'Tarjeta' },
              ]}
              value={editingCobro.forma_pago}
              onChange={(e) => setEditingCobro({ ...editingCobro, forma_pago: e.target.value as Cobro['forma_pago'] })}
            />
            <Textarea
              label="Observaciones"
              value={editingCobro.observaciones ?? ''}
              onChange={(e) => setEditingCobro({ ...editingCobro, observaciones: e.target.value || null })}
            />
            <div className="flex gap-3 pt-4">
              <Button variant="primary" onClick={handleSaveEdit} className="flex-1" disabled={saving}>
                {saving ? 'Guardando...' : 'Guardar cambios'}
              </Button>
              <Button variant="secondary" onClick={() => setEditingCobro(null)} className="flex-1">
                Cancelar
              </Button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
}
