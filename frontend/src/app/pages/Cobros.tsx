import { useState, useEffect, useMemo } from "react";
import { DollarSign, Building2, FileText, CreditCard, Search } from "lucide-react";
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
  const [activeTab, setActiveTab] = useState<'lista' | 'saldos' | 'registrar'>('lista');
  const [cobros, setCobros] = useState<Cobro[]>([]);
  const [ventas, setVentas] = useState<Venta[]>([]);
  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterVenta, setFilterVenta] = useState<string>('todos');
  const [filterConcepto, setFilterConcepto] = useState('todos');
  const [filterFormaPago, setFilterFormaPago] = useState('todos');
  const [filterDesde, setFilterDesde] = useState('');
  const [filterHasta, setFilterHasta] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
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

  const getCliente = (id: number) => clientes.find((c) => c.id === id);
  const getVenta = (id: number) => ventas.find((v) => v.id === id);

  const filteredCobros = useMemo(() => {
    const q = searchTerm.toLowerCase();
    return [...cobros]
      .sort((a, b) => new Date(b.fecha).getTime() - new Date(a.fecha).getTime())
      .filter((cobro) => {
        const cliente = getCliente(cobro.cliente_id);
        const matchVenta = filterVenta === 'todos' || cobro.venta_id === parseInt(filterVenta);
        const matchConcepto = filterConcepto === 'todos' || cobro.concepto === filterConcepto;
        const matchPago = filterFormaPago === 'todos' || cobro.forma_pago === filterFormaPago;
        const matchDesde = !filterDesde || cobro.fecha >= filterDesde;
        const matchHasta = !filterHasta || cobro.fecha <= filterHasta + 'T23:59:59';
        const matchSearch = !q ||
          cliente?.nombre.toLowerCase().includes(q) ||
          cliente?.apellido.toLowerCase().includes(q);
        return matchVenta && matchConcepto && matchPago && matchDesde && matchHasta && matchSearch;
      });
  }, [cobros, clientes, filterVenta, filterConcepto, filterFormaPago, filterDesde, filterHasta, searchTerm]);

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
          {(['lista', 'saldos', 'registrar'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`pb-3 px-1 border-b-2 font-medium transition-colors ${
                activeTab === tab
                  ? 'border-[#FF6B2B] text-[#FF6B2B]'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              {tab === 'lista' ? 'Lista' : tab === 'saldos' ? 'Saldos pendientes' : 'Registrar'}
            </button>
          ))}
        </div>
      </div>

      {activeTab === 'lista' && (
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                placeholder="Buscar cliente..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-9 pr-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#FF6B2B]"
              />
            </div>
            <select value={filterConcepto} onChange={(e) => setFilterConcepto(e.target.value)}
              className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#FF6B2B]">
              <option value="todos">Todos los conceptos</option>
              <option value="sena">Seña</option>
              <option value="saldo">Saldo</option>
              <option value="cuota">Cuota</option>
              <option value="otro">Otro</option>
            </select>
            <select value={filterFormaPago} onChange={(e) => setFilterFormaPago(e.target.value)}
              className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#FF6B2B]">
              <option value="todos">Todas las formas de pago</option>
              <option value="efectivo">Efectivo</option>
              <option value="transferencia">Transferencia</option>
              <option value="cheque">Cheque</option>
              <option value="tarjeta">Tarjeta</option>
            </select>
            <div className="flex gap-2">
              <input type="date" value={filterDesde} onChange={(e) => setFilterDesde(e.target.value)}
                className="flex-1 border border-gray-300 rounded-lg px-2 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#FF6B2B]" title="Desde" />
              <input type="date" value={filterHasta} onChange={(e) => setFilterHasta(e.target.value)}
                className="flex-1 border border-gray-300 rounded-lg px-2 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#FF6B2B]" title="Hasta" />
            </div>
          </div>

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
                <div className="p-8 text-center text-gray-500">
                  {cobros.length === 0 ? 'No hay cobros registrados' : 'Sin resultados para los filtros aplicados'}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {activeTab === 'saldos' && (() => {
        const saldos = ventas
          .map((venta) => {
            const ventaCobros = cobros.filter((c) => c.venta_id === venta.id);
            const cobrado = ventaCobros.reduce((s, c) => s + parseDecimal(c.monto), 0);
            const saldo = parseDecimal(venta.precio_final) - cobrado;
            return { venta, cobrado, saldo };
          })
          .filter(({ saldo }) => saldo > 0.01)
          .sort((a, b) => b.saldo - a.saldo);

        const totalSaldo = saldos.reduce((s, { saldo }) => s + saldo, 0);

        return (
          <div className="space-y-4">
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex justify-between items-center">
              <p className="font-semibold text-red-800">{saldos.length} venta{saldos.length !== 1 ? 's' : ''} con saldo pendiente</p>
              <p className="text-xl font-bold text-red-700">{formatCurrency(totalSaldo)}</p>
            </div>
            {saldos.length === 0 ? (
              <div className="bg-white rounded-lg border border-gray-200 p-8 text-center text-gray-500">
                Todas las ventas están saldadas
              </div>
            ) : (
              <div className="bg-white rounded-lg border border-gray-200 shadow-sm divide-y divide-gray-200">
                {saldos.map(({ venta, cobrado, saldo }) => {
                  const cliente = clientes.find((c) => c.id === venta.cliente_id);
                  return (
                    <div key={venta.id} className="p-4 hover:bg-gray-50 transition-colors">
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-center">
                        <div>
                          <h3 className="font-semibold text-gray-900">
                            {cliente ? `${cliente.apellido.toUpperCase()}, ${cliente.nombre}` : `Cliente #${venta.cliente_id}`}
                          </h3>
                          <p className="text-sm text-gray-500">Venta #{venta.id} · {formatDate(venta.fecha_venta)}</p>
                        </div>
                        <div className="text-sm space-y-0.5">
                          <div className="flex justify-between">
                            <span className="text-gray-500">Precio</span>
                            <span className="font-medium">{formatCurrency(parseDecimal(venta.precio_final))}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-500">Cobrado</span>
                            <span className="text-green-700 font-medium">{formatCurrency(cobrado)}</span>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="text-xl font-bold text-red-600">{formatCurrency(saldo)}</p>
                          <p className="text-xs text-gray-500">pendiente</p>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        );
      })()}

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
