import { useState, useEffect } from "react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, PieChart, Pie, Cell,
} from 'recharts';
import { toast } from "sonner";
import { api, parseDecimal } from "../api";
import type { Venta, Cobro, Vehiculo, Cheque } from "../api";
import { formatCurrency, formatDate } from "../lib/utils";
import StatusBadge from "../components/StatusBadge";
import Select from "../components/Select";
import Button from "../components/Button";

function getLast6Months(): string[] {
  const months: string[] = [];
  const now = new Date();
  for (let i = 5; i >= 0; i--) {
    const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
    months.push(
      `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
    );
  }
  return months;
}

export default function Dashboard() {
  const [ventas, setVentas] = useState<Venta[]>([]);
  const [cobros, setCobros] = useState<Cobro[]>([]);
  const [vehiculos, setVehiculos] = useState<Vehiculo[]>([]);
  const [chequesData, setChequesData] = useState<Cheque[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState<number | null>(null);

  useEffect(() => {
    Promise.all([
      api.get('/ventas/'),
      api.get('/cobros/'),
      api.get('/vehiculos/'),
      api.get('/cheques/', { estado: 'pendiente' }),
    ])
      .then(([v, c, veh, ch]) => {
        setVentas(v);
        setCobros(c);
        setVehiculos(veh);
        setChequesData(ch);
      })
      .catch((e) => toast.error(e.message))
      .finally(() => setLoading(false));
  }, []);

  const now = new Date();
  const currentYM = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
  const prevDate = new Date(now.getFullYear(), now.getMonth() - 1, 1);
  const prevYM = `${prevDate.getFullYear()}-${String(prevDate.getMonth() + 1).padStart(2, '0')}`;

  const cobrosMes = cobros.filter((c) => c.fecha.startsWith(currentYM));
  const cobrosPrevMes = cobros.filter((c) => c.fecha.startsWith(prevYM));
  const totalCobradoMes = cobrosMes.reduce((s, c) => s + parseDecimal(c.monto), 0);
  const totalCobradoPrev = cobrosPrevMes.reduce((s, c) => s + parseDecimal(c.monto), 0);
  const cobradoDeltaPct =
    totalCobradoPrev > 0
      ? ((totalCobradoMes - totalCobradoPrev) / totalCobradoPrev) * 100
      : null;

  const ventasMes = ventas.filter((v) => v.fecha_venta.startsWith(currentYM)).length;
  const ventasPrevMes = ventas.filter((v) => v.fecha_venta.startsWith(prevYM)).length;

  const margenBrutoMes = ventas
    .filter((v) => v.fecha_venta.startsWith(currentYM))
    .reduce((sum, v) => {
      const vehiculo = vehiculos.find((veh) => veh.id === v.vehiculo_id);
      return sum + (parseDecimal(v.precio_final) - parseDecimal(vehiculo?.precio_compra));
    }, 0);

  const cheques30d = chequesData
    .filter((ch) => {
      const diff = new Date(ch.fecha_cobro).getTime() - now.getTime();
      const days = diff / (1000 * 60 * 60 * 24);
      return days <= 30 && days >= 0;
    })
    .reduce((sum, ch) => sum + parseDecimal(ch.monto), 0);

  const last6 = getLast6Months();

  const cobrosPorMes = last6.map((mes) => {
    const cm = cobros.filter((c) => c.fecha.startsWith(mes));
    return {
      mes,
      efectivo: cm.filter((c) => c.forma_pago === 'efectivo').reduce((s, c) => s + parseDecimal(c.monto), 0),
      transferencia: cm.filter((c) => c.forma_pago === 'transferencia').reduce((s, c) => s + parseDecimal(c.monto), 0),
      cheque: cm.filter((c) => c.forma_pago === 'cheque').reduce((s, c) => s + parseDecimal(c.monto), 0),
      tarjeta: cm.filter((c) => c.forma_pago === 'tarjeta').reduce((s, c) => s + parseDecimal(c.monto), 0),
    };
  });

  const facturacionPorMes = last6.map((mes) => {
    const vm = ventas.filter((v) => v.fecha_venta.startsWith(mes));
    return {
      mes,
      facturado: vm.reduce((s, v) => s + parseDecimal(v.precio_final), 0),
      ventas: vm.length,
    };
  });

  const cobrosPorFormaPago = [
    { name: 'Efectivo', value: cobros.filter((c) => c.forma_pago === 'efectivo').reduce((s, c) => s + parseDecimal(c.monto), 0), color: '#10b981' },
    { name: 'Transferencia', value: cobros.filter((c) => c.forma_pago === 'transferencia').reduce((s, c) => s + parseDecimal(c.monto), 0), color: '#3b82f6' },
    { name: 'Cheque', value: cobros.filter((c) => c.forma_pago === 'cheque').reduce((s, c) => s + parseDecimal(c.monto), 0), color: '#f59e0b' },
    { name: 'Tarjeta', value: cobros.filter((c) => c.forma_pago === 'tarjeta').reduce((s, c) => s + parseDecimal(c.monto), 0), color: '#8b5cf6' },
  ];

  const stockPorEstado = [
    { name: 'Disponible', value: vehiculos.filter((v) => v.estado === 'disponible').length, color: '#10b981' },
    { name: 'Reservado', value: vehiculos.filter((v) => v.estado === 'reservado').length, color: '#f59e0b' },
    { name: 'Vendido', value: vehiculos.filter((v) => v.estado === 'vendido').length, color: '#6b7280' },
  ];

  const margenPorVenta = ventas.slice(-10).map((v) => {
    const vehiculo = vehiculos.find((veh) => veh.id === v.vehiculo_id);
    const margen = parseDecimal(v.precio_final) - parseDecimal(vehiculo?.precio_compra);
    return {
      name: `${vehiculo?.marca ?? '?'} ${vehiculo?.modelo ?? '?'} (#${v.id})`,
      margen,
    };
  });

  const chequesVencidos = chequesData
    .filter((ch) => new Date(ch.fecha_cobro).getTime() < now.getTime())
    .sort((a, b) => new Date(a.fecha_cobro).getTime() - new Date(b.fecha_cobro).getTime());

  const chequesPor7d = chequesData
    .filter((ch) => {
      const diff = new Date(ch.fecha_cobro).getTime() - now.getTime();
      const days = diff / (1000 * 60 * 60 * 24);
      return days >= 0 && days <= 7;
    })
    .sort((a, b) => new Date(a.fecha_cobro).getTime() - new Date(b.fecha_cobro).getTime());

  const chequesProximos = chequesData
    .filter((ch) => {
      const diff = new Date(ch.fecha_cobro).getTime() - now.getTime();
      const days = diff / (1000 * 60 * 60 * 24);
      return days <= 30 && days >= 0;
    })
    .sort((a, b) => new Date(a.fecha_cobro).getTime() - new Date(b.fecha_cobro).getTime())
    .slice(0, 4);

  const getDaysUntil = (date: string) => {
    const diff = new Date(date).getTime() - now.getTime();
    return Math.ceil(diff / (1000 * 60 * 60 * 24));
  };

  const handleUpdateChequeEstado = (chequeId: number, nuevoEstado: string) => {
    setChequesData((prev) =>
      prev.map((ch) =>
        ch.id === chequeId
          ? { ...ch, estado: nuevoEstado as Cheque['estado'] }
          : ch
      )
    );
  };

  const handleSaveChequeEstado = async (chequeId: number) => {
    const cheque = chequesData.find((ch) => ch.id === chequeId);
    if (!cheque) return;
    setSaving(chequeId);
    try {
      await api.patch(`/cheques/${chequeId}`, { estado: cheque.estado });
      toast.success('Estado actualizado');
    } catch (e: any) {
      toast.error(e.message);
    } finally {
      setSaving(null);
    }
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto space-y-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="bg-white rounded-lg border border-gray-200 shadow-sm p-6 animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-2/3 mb-3" />
              <div className="h-8 bg-gray-200 rounded w-1/2" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>

      {chequesVencidos.length > 0 && (
        <div className="bg-red-50 border border-red-300 rounded-lg p-4 flex items-start gap-3">
          <span className="text-red-500 text-xl leading-none">⚠</span>
          <div>
            <p className="font-semibold text-red-800">
              {chequesVencidos.length} cheque{chequesVencidos.length > 1 ? 's' : ''} vencido{chequesVencidos.length > 1 ? 's' : ''} sin cobrar
            </p>
            <p className="text-sm text-red-700 mt-0.5">
              {chequesVencidos.map((ch) => `#${ch.id} — ${formatCurrency(parseDecimal(ch.monto))} (venció ${formatDate(ch.fecha_cobro)})`).join(' · ')}
            </p>
          </div>
        </div>
      )}

      {chequesPor7d.length > 0 && (
        <div className="bg-amber-50 border border-amber-300 rounded-lg p-4 flex items-start gap-3">
          <span className="text-amber-500 text-xl leading-none">⏰</span>
          <div>
            <p className="font-semibold text-amber-800">
              {chequesPor7d.length} cheque{chequesPor7d.length > 1 ? 's' : ''} vence{chequesPor7d.length > 1 ? 'n' : ''} en los próximos 7 días
            </p>
            <p className="text-sm text-amber-700 mt-0.5">
              {chequesPor7d.map((ch) => `#${ch.id} — ${formatCurrency(parseDecimal(ch.monto))} (${formatDate(ch.fecha_cobro)})`).join(' · ')}
            </p>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
          <p className="text-sm text-gray-500 mb-1">Cobrado este mes</p>
          <p className="text-2xl font-bold text-gray-900">{formatCurrency(totalCobradoMes)}</p>
          {cobradoDeltaPct !== null && (
            <p className={`text-sm mt-1 ${cobradoDeltaPct >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {cobradoDeltaPct >= 0 ? '↑' : '↓'} {Math.abs(cobradoDeltaPct).toFixed(0)}% vs mes anterior
            </p>
          )}
        </div>

        <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
          <p className="text-sm text-gray-500 mb-1">Ventas del mes</p>
          <p className="text-2xl font-bold text-gray-900">{ventasMes}</p>
          <p className={`text-sm mt-1 ${ventasMes >= ventasPrevMes ? 'text-green-600' : 'text-red-600'}`}>
            {ventasMes >= ventasPrevMes ? '↑' : '↓'} {Math.abs(ventasMes - ventasPrevMes)} vs mes anterior
          </p>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
          <p className="text-sm text-gray-500 mb-1">Margen bruto del mes</p>
          <p className={`text-2xl font-bold ${margenBrutoMes >= 0 ? 'text-gray-900' : 'text-red-600'}`}>
            {formatCurrency(margenBrutoMes)}
          </p>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
          <p className="text-sm text-gray-500 mb-1">Cheques a cobrar (30d)</p>
          <p className="text-2xl font-bold text-gray-900">{formatCurrency(cheques30d)}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Cobros por mes — últimos 6 meses
          </h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={cobrosPorMes}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="mes" />
              <YAxis />
              <Tooltip formatter={(value) => formatCurrency(value as number)} />
              <Legend />
              <Bar dataKey="efectivo" stackId="a" fill="#10b981" name="Efectivo" />
              <Bar dataKey="transferencia" stackId="a" fill="#3b82f6" name="Transferencia" />
              <Bar dataKey="cheque" stackId="a" fill="#f59e0b" name="Cheque" />
              <Bar dataKey="tarjeta" stackId="a" fill="#8b5cf6" name="Tarjeta" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Facturación por mes — últimos 6 meses
          </h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={facturacionPorMes}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="mes" />
              <YAxis />
              <Tooltip formatter={(value) => formatCurrency(value as number)} />
              <Bar dataKey="facturado" fill="#FF6B2B" label={{
                position: 'top',
                content: (props: any) => {
                  const d = facturacionPorMes[props.index];
                  if (!d?.ventas) return null;
                  return (
                    <text
                      x={(props.x || 0) + (props.width || 0) / 2}
                      y={(props.y || 0) - 5}
                      fill="#6b7280"
                      textAnchor="middle"
                      fontSize={11}
                    >
                      {d.ventas} ventas
                    </text>
                  );
                },
              }}>
                {facturacionPorMes.map((_, index) => (
                  <Cell key={`cell-${index}`} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Cobros por forma de pago
          </h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={cobrosPorFormaPago}
                cx="50%"
                cy="50%"
                labelLine={true}
                label={(entry) => `${entry.name}: ${formatCurrency(entry.value)}`}
                outerRadius={80}
                dataKey="value"
              >
                {cobrosPorFormaPago.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip formatter={(value) => formatCurrency(value as number)} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Stock actual por estado
          </h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={stockPorEstado}
                cx="50%"
                cy="50%"
                labelLine={true}
                label={(entry) => `${entry.name}: ${entry.value}`}
                outerRadius={80}
                dataKey="value"
              >
                {stockPorEstado.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Margen por venta — últimas 10 operaciones
        </h2>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={margenPorVenta} layout="vertical">
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis type="number" />
            <YAxis dataKey="name" type="category" width={150} />
            <Tooltip formatter={(value) => formatCurrency(value as number)} />
            <Bar dataKey="margen" fill="#10b981">
              {margenPorVenta.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.margen >= 0 ? '#10b981' : '#ef4444'} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-2">
          Cheques pendientes — próximos 30 días
        </h2>
        <p className="text-sm text-gray-500 mb-4">
          Total a cobrar: {formatCurrency(cheques30d)}
        </p>

        {chequesProximos.length > 0 ? (
          <div className="space-y-4">
            {chequesProximos.map((cheque) => {
              const days = getDaysUntil(cheque.fecha_cobro);
              return (
                <div
                  key={cheque.id}
                  className="grid grid-cols-1 md:grid-cols-4 gap-4 items-center border-b border-gray-200 pb-4 last:border-b-0"
                >
                  <div className="text-center md:text-left">
                    <p
                      className={`text-3xl font-bold ${
                        days <= 3 ? 'text-red-600' : days <= 7 ? 'text-amber-600' : 'text-gray-600'
                      }`}
                    >
                      {days === 0 ? 'hoy' : `${days}d`}
                    </p>
                  </div>

                  <div className="md:col-span-2">
                    <p className="font-semibold text-gray-900">
                      {cheque.banco} - {cheque.numero}
                    </p>
                    <p className="text-sm text-gray-500">
                      {cheque.titular} · {formatDate(cheque.fecha_cobro)}
                    </p>
                    <p className="font-medium text-gray-800">{formatCurrency(parseDecimal(cheque.monto))}</p>
                  </div>

                  <div className="flex gap-2 items-center">
                    <Select
                      options={[
                        { value: 'pendiente', label: 'Pendiente' },
                        { value: 'cobrado', label: 'Cobrado' },
                        { value: 'depositado', label: 'Depositado' },
                        { value: 'rechazado', label: 'Rechazado' },
                      ]}
                      value={cheque.estado}
                      onChange={(e) => handleUpdateChequeEstado(cheque.id, e.target.value)}
                      className="flex-1"
                    />
                    <Button
                      variant="primary"
                      className="whitespace-nowrap"
                      disabled={saving === cheque.id}
                      onClick={() => handleSaveChequeEstado(cheque.id)}
                    >
                      {saving === cheque.id ? '...' : 'Guardar'}
                    </Button>
                  </div>
                </div>
              );
            })}

            {chequesData.filter((ch) => {
              const diff = new Date(ch.fecha_cobro).getTime() - now.getTime();
              const days = diff / (1000 * 60 * 60 * 24);
              return days <= 30 && days >= 0;
            }).length > 4 && (
              <p className="text-sm text-gray-600 mt-4">
                +{
                  chequesData.filter((ch) => {
                    const diff = new Date(ch.fecha_cobro).getTime() - now.getTime();
                    const days = diff / (1000 * 60 * 60 * 24);
                    return days <= 30 && days >= 0;
                  }).length - 4
                } cheques más — ver todos en la sección Cheques.
              </p>
            )}
          </div>
        ) : (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-center">
            <p className="text-green-700">
              No hay cheques venciendo en los próximos 30 días.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
