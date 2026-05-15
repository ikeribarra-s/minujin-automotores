import { useState, useEffect } from "react";
import { Upload, ScanLine } from "lucide-react";
import { toast } from "sonner";
import { api, uploadFile, parseDecimal } from "../api";
import type { Cheque, ScanResult } from "../api";
import { formatCurrency, formatDate } from "../lib/utils";
import StatusBadge from "../components/StatusBadge";
import Button from "../components/Button";
import Input from "../components/Input";
import Select from "../components/Select";
import Textarea from "../components/Textarea";
import Modal from "../components/Modal";

interface ScanFormData {
  tipo: string;
  numero: string;
  banco: string;
  titular: string;
  entrega: string;
  monto: string;
  monto_letras: string;
  fecha_emision: string;
  fecha_cobro: string;
  pagador_cuit: string;
  beneficiario: string;
  sucursal: string;
  localidad: string;
  es_cpd: boolean;
  discrepancia_monto: boolean;
  observaciones: string;
  raw_ocr_text: string;
  warning: string | null;
}

function scanResultToForm(r: ScanResult): ScanFormData {
  return {
    tipo: r.tipo ?? 'cheque',
    numero: r.numero ?? '',
    banco: r.banco ?? '',
    titular: r.pagador_nombre ?? '',
    entrega: '',
    monto: r.monto_numerico ?? '',
    monto_letras: r.monto_letras ?? '',
    fecha_emision: r.fecha_emision ?? '',
    fecha_cobro: r.fecha_vencimiento ?? '',
    pagador_cuit: r.pagador_cuit ?? '',
    beneficiario: r.beneficiario ?? '',
    sucursal: r.sucursal ?? '',
    localidad: r.localidad ?? '',
    es_cpd: r.es_cpd,
    discrepancia_monto: r.discrepancia_monto,
    observaciones: '',
    raw_ocr_text: r.raw_ocr_text,
    warning: r.warning,
  };
}

const emptyCheque = {
  numero: '',
  banco: '',
  titular: '',
  entrega: '',
  monto: '',
  fecha_cobro: '',
  fecha_emision: '',
};

export default function Cheques() {
  const [activeTab, setActiveTab] = useState<'cartera' | 'escanear' | 'registrar'>('cartera');
  const [cheques, setCheques] = useState<Cheque[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>('todos');
  const [editingCheque, setEditingCheque] = useState<Cheque | null>(null);
  const [saving, setSaving] = useState(false);

  const [uploadedImage, setUploadedImage] = useState<string | null>(null);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [scanningInProgress, setScanningInProgress] = useState(false);
  const [scanForm, setScanForm] = useState<ScanFormData | null>(null);

  const [nuevoCheque, setNuevoCheque] = useState(emptyCheque);

  useEffect(() => {
    api
      .get('/cheques/')
      .then(setCheques)
      .catch((e) => toast.error(e.message))
      .finally(() => setLoading(false));
  }, []);

  const filteredCheques = cheques.filter((cheque) =>
    filter === 'todos' ? true : cheque.estado === filter
  );

  const handleEditCheque = (cheque: Cheque) => setEditingCheque(cheque);

  const handleSaveEdit = async () => {
    if (!editingCheque) return;
    setSaving(true);
    try {
      const updated = await api.patch(`/cheques/${editingCheque.id}`, {
        numero: editingCheque.numero,
        banco: editingCheque.banco,
        titular: editingCheque.titular || undefined,
        entrega: editingCheque.entrega || undefined,
        monto: parseDecimal(editingCheque.monto),
        estado: editingCheque.estado,
        fecha_emision: editingCheque.fecha_emision || undefined,
        fecha_cobro: editingCheque.fecha_cobro,
        es_cpd: editingCheque.es_cpd,
        discrepancia_monto: editingCheque.discrepancia_monto,
        monto_letras: editingCheque.monto_letras || undefined,
        observaciones: editingCheque.observaciones || undefined,
      }) as Cheque;
      setCheques((prev) => prev.map((c) => (c.id === updated.id ? updated : c)));
      setEditingCheque(null);
      toast.success('Cheque actualizado');
    } catch (e: any) {
      toast.error(e.message);
    } finally {
      setSaving(false);
    }
  };

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploadedFile(file);
    const reader = new FileReader();
    reader.onload = (event) => setUploadedImage(event.target?.result as string);
    reader.readAsDataURL(file);
  };

  const handleScanDocument = async () => {
    if (!uploadedFile) return;
    setScanningInProgress(true);
    try {
      const result = await uploadFile('/cheques/scan', uploadedFile, 120_000) as ScanResult;
      setScanForm(scanResultToForm(result));
    } catch (e: any) {
      toast.error(e.message);
    } finally {
      setScanningInProgress(false);
    }
  };

  const handleGuardarChequeEscaneado = async () => {
    if (!scanForm) return;
    setSaving(true);
    try {
      const created = await api.post('/cheques/', {
        numero: scanForm.numero,
        banco: scanForm.banco,
        monto: parseFloat(scanForm.monto) || 0,
        fecha_cobro: scanForm.fecha_cobro,
        titular: scanForm.titular || undefined,
        entrega: scanForm.entrega || undefined,
        fecha_emision: scanForm.fecha_emision || undefined,
        monto_letras: scanForm.monto_letras || undefined,
        pagador_cuit: scanForm.pagador_cuit || undefined,
        beneficiario: scanForm.beneficiario || undefined,
        sucursal: scanForm.sucursal || undefined,
        localidad: scanForm.localidad || undefined,
        es_cpd: scanForm.es_cpd,
        discrepancia_monto: scanForm.discrepancia_monto,
        observaciones: scanForm.observaciones || undefined,
        raw_ocr_text: scanForm.raw_ocr_text || undefined,
      }) as Cheque;
      setCheques((prev) => [created, ...prev]);
      setUploadedImage(null);
      setUploadedFile(null);
      setScanForm(null);
      setActiveTab('cartera');
      toast.success('Cheque guardado');
    } catch (e: any) {
      toast.error(e.message);
    } finally {
      setSaving(false);
    }
  };

  const handleRegistrarCheque = async () => {
    if (!nuevoCheque.numero || !nuevoCheque.banco || !nuevoCheque.monto || !nuevoCheque.fecha_cobro) {
      toast.error('Número, banco, monto y fecha de cobro son obligatorios');
      return;
    }
    setSaving(true);
    try {
      const created = await api.post('/cheques/', {
        numero: nuevoCheque.numero,
        banco: nuevoCheque.banco,
        monto: parseFloat(nuevoCheque.monto),
        fecha_cobro: nuevoCheque.fecha_cobro,
        titular: nuevoCheque.titular || undefined,
        entrega: nuevoCheque.entrega || undefined,
        fecha_emision: nuevoCheque.fecha_emision || undefined,
      }) as Cheque;
      setCheques((prev) => [created, ...prev]);
      setNuevoCheque(emptyCheque);
      setActiveTab('cartera');
      toast.success('Cheque registrado');
    } catch (e: any) {
      toast.error(e.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">Cartera de Cheques</h1>

      <div className="border-b border-gray-200">
        <div className="flex gap-6">
          {([['cartera', 'Cartera'], ['escanear', 'Escanear'], ['registrar', 'Registrar manual']] as const).map(([tab, label]) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`pb-3 px-1 border-b-2 font-medium transition-colors ${
                activeTab === tab
                  ? 'border-[#FF6B2B] text-[#FF6B2B]'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      {activeTab === 'cartera' && (
        <div className="space-y-4">
          <Select
            options={[
              { value: 'todos', label: 'Todos' },
              { value: 'pendiente', label: 'Pendiente' },
              { value: 'cobrado', label: 'Cobrado' },
              { value: 'depositado', label: 'Depositado' },
              { value: 'rechazado', label: 'Rechazado' },
            ]}
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="max-w-xs"
          />

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
              {filteredCheques.map((cheque) => (
                <div key={cheque.id} className="p-4 hover:bg-gray-50 transition-colors">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-center">
                    <div>
                      <h3 className="font-semibold text-gray-900">
                        {cheque.banco} N° {cheque.numero}
                      </h3>
                      <p className="text-sm text-gray-600">
                        {cheque.titular}
                        {cheque.entrega && ` · ${cheque.entrega}`}
                      </p>
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-gray-900">
                        {formatCurrency(parseDecimal(cheque.monto))}
                      </p>
                      <p className="text-sm text-gray-500">{formatDate(cheque.fecha_cobro)}</p>
                      <StatusBadge status={cheque.estado} className="mt-2" />
                    </div>
                    <div className="flex justify-end">
                      <Button variant="secondary" onClick={() => handleEditCheque(cheque)}>
                        Editar
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
              {filteredCheques.length === 0 && (
                <div className="p-8 text-center text-gray-500">No hay cheques registrados</div>
              )}
            </div>
          )}
        </div>
      )}

      {activeTab === 'escanear' && (
        <div className="space-y-6">
          <div>
            <h2 className="text-xl font-semibold text-gray-900 mb-2">Escanear cheque o pagaré</h2>
            <p className="text-sm text-gray-600">
              Subí una foto del documento. La IA extraerá los datos automáticamente.
            </p>
          </div>

          {!scanForm ? (
            <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6 space-y-4">
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
                <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-sm text-gray-600 mb-2">Formatos aceptados: JPG, JPEG, PNG, WEBP</p>
                <input
                  type="file"
                  accept="image/jpeg,image/jpg,image/png,image/webp"
                  className="hidden"
                  id="cheque-upload"
                  onChange={handleImageUpload}
                />
                <label htmlFor="cheque-upload">
                  <Button variant="secondary" className="cursor-pointer">
                    Seleccionar archivo
                  </Button>
                </label>
              </div>

              {uploadedImage && (
                <div className="space-y-4">
                  <div className="rounded-lg overflow-hidden border border-gray-200">
                    <img src={uploadedImage} alt="Cheque escaneado" className="w-full" />
                  </div>
                  <Button
                    variant="primary"
                    onClick={handleScanDocument}
                    disabled={scanningInProgress}
                    className="w-full"
                  >
                    {scanningInProgress ? (
                      <span className="flex items-center justify-center gap-2">
                        <ScanLine className="w-5 h-5 animate-pulse" />
                        Procesando con IA...
                      </span>
                    ) : (
                      'Escanear documento'
                    )}
                  </Button>
                </div>
              )}
            </div>
          ) : (
            <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6 space-y-4">
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <p className="text-green-800 font-medium">
                  Datos extraídos. Revisá y completá los campos faltantes.
                </p>
              </div>

              {scanForm.warning && (
                <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
                  <p className="text-amber-800 text-sm">{scanForm.warning}</p>
                </div>
              )}

              <details className="border border-gray-200 rounded-lg p-4">
                <summary className="cursor-pointer font-medium text-gray-900">Ver OCR completo</summary>
                <pre className="mt-3 text-xs text-gray-600 whitespace-pre-wrap bg-gray-50 p-3 rounded">
                  {scanForm.raw_ocr_text}
                </pre>
              </details>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Select
                  label="Tipo"
                  options={[{ value: 'cheque', label: 'Cheque' }, { value: 'pagare', label: 'Pagaré' }]}
                  value={scanForm.tipo === 'pagare' ? 'pagare' : 'cheque'}
                  onChange={(e) => setScanForm({ ...scanForm, tipo: e.target.value })}
                />
                <Input label="Número" value={scanForm.numero} onChange={(e) => setScanForm({ ...scanForm, numero: e.target.value })} />
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input label="Banco" value={scanForm.banco} onChange={(e) => setScanForm({ ...scanForm, banco: e.target.value })} />
                <Input label="Titular / Pagador" value={scanForm.titular} onChange={(e) => setScanForm({ ...scanForm, titular: e.target.value })} />
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input label="Monto $" type="number" value={scanForm.monto} onChange={(e) => setScanForm({ ...scanForm, monto: e.target.value })} />
                <Input label="CUIT pagador" value={scanForm.pagador_cuit} onChange={(e) => setScanForm({ ...scanForm, pagador_cuit: e.target.value })} />
              </div>
              <Input label="Monto en letras" value={scanForm.monto_letras} onChange={(e) => setScanForm({ ...scanForm, monto_letras: e.target.value })} />
              <Input label="Beneficiario" value={scanForm.beneficiario} onChange={(e) => setScanForm({ ...scanForm, beneficiario: e.target.value })} />
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input label="Sucursal" value={scanForm.sucursal} onChange={(e) => setScanForm({ ...scanForm, sucursal: e.target.value })} />
                <Input label="Localidad" value={scanForm.localidad} onChange={(e) => setScanForm({ ...scanForm, localidad: e.target.value })} />
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input label="Fecha emisión" type="date" value={scanForm.fecha_emision} onChange={(e) => setScanForm({ ...scanForm, fecha_emision: e.target.value })} />
                <Input label="Fecha vencimiento/cobro" type="date" value={scanForm.fecha_cobro} onChange={(e) => setScanForm({ ...scanForm, fecha_cobro: e.target.value })} />
              </div>
              <Input label="Entrega" value={scanForm.entrega} onChange={(e) => setScanForm({ ...scanForm, entrega: e.target.value })} />
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="cpd"
                  checked={scanForm.es_cpd}
                  onChange={(e) => setScanForm({ ...scanForm, es_cpd: e.target.checked })}
                  className="w-4 h-4 text-[#FF6B2B] border-gray-300 rounded focus:ring-[#FF6B2B]"
                />
                <label htmlFor="cpd" className="text-sm text-gray-700">CPD</label>
              </div>
              <Textarea label="Observaciones" value={scanForm.observaciones} onChange={(e) => setScanForm({ ...scanForm, observaciones: e.target.value })} />
              <div className="flex gap-3">
                <Button variant="primary" onClick={handleGuardarChequeEscaneado} className="flex-1" disabled={saving}>
                  {saving ? 'Guardando...' : 'Guardar cheque'}
                </Button>
                <Button variant="secondary" onClick={() => { setScanForm(null); setUploadedImage(null); setUploadedFile(null); }} className="flex-1">
                  Cancelar
                </Button>
              </div>
            </div>
          )}
        </div>
      )}

      {activeTab === 'registrar' && (
        <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <Input label="Número" value={nuevoCheque.numero} onChange={(e) => setNuevoCheque({ ...nuevoCheque, numero: e.target.value })} required />
            <Input label="Banco" value={nuevoCheque.banco} onChange={(e) => setNuevoCheque({ ...nuevoCheque, banco: e.target.value })} required />
          </div>
          <Input label="Titular" value={nuevoCheque.titular} onChange={(e) => setNuevoCheque({ ...nuevoCheque, titular: e.target.value })} className="mb-4" />
          <Input label="Entrega" value={nuevoCheque.entrega} onChange={(e) => setNuevoCheque({ ...nuevoCheque, entrega: e.target.value })} className="mb-4" />
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <Input label="Monto" type="number" value={nuevoCheque.monto} onChange={(e) => setNuevoCheque({ ...nuevoCheque, monto: e.target.value })} required />
            <Input label="Fecha de cobro" type="date" value={nuevoCheque.fecha_cobro} onChange={(e) => setNuevoCheque({ ...nuevoCheque, fecha_cobro: e.target.value })} required />
          </div>
          <Input label="Fecha de emisión (opcional)" type="date" value={nuevoCheque.fecha_emision} onChange={(e) => setNuevoCheque({ ...nuevoCheque, fecha_emision: e.target.value })} className="mb-4" />
          <Button variant="primary" onClick={handleRegistrarCheque} className="w-full" disabled={saving}>
            {saving ? 'Registrando...' : 'Registrar cheque'}
          </Button>
        </div>
      )}

      {editingCheque && (
        <Modal isOpen={true} onClose={() => setEditingCheque(null)} title="Editar cheque">
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input label="Número" value={editingCheque.numero} onChange={(e) => setEditingCheque({ ...editingCheque, numero: e.target.value })} />
              <Input label="Banco" value={editingCheque.banco} onChange={(e) => setEditingCheque({ ...editingCheque, banco: e.target.value })} />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input label="Titular" value={editingCheque.titular ?? ''} onChange={(e) => setEditingCheque({ ...editingCheque, titular: e.target.value || null })} />
              <Input label="Entrega" value={editingCheque.entrega ?? ''} onChange={(e) => setEditingCheque({ ...editingCheque, entrega: e.target.value || null })} />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input label="Monto $" type="number" value={editingCheque.monto} onChange={(e) => setEditingCheque({ ...editingCheque, monto: e.target.value })} />
              <Select
                label="Estado"
                options={[
                  { value: 'pendiente', label: 'Pendiente' },
                  { value: 'cobrado', label: 'Cobrado' },
                  { value: 'depositado', label: 'Depositado' },
                  { value: 'rechazado', label: 'Rechazado' },
                ]}
                value={editingCheque.estado}
                onChange={(e) => setEditingCheque({ ...editingCheque, estado: e.target.value as Cheque['estado'] })}
              />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input label="Fecha emisión" type="date" value={editingCheque.fecha_emision ?? ''} onChange={(e) => setEditingCheque({ ...editingCheque, fecha_emision: e.target.value || null })} />
              <Input label="Fecha cobro" type="date" value={editingCheque.fecha_cobro} onChange={(e) => setEditingCheque({ ...editingCheque, fecha_cobro: e.target.value })} />
            </div>
            <div className="flex items-center gap-6">
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="edit-cpd"
                  checked={editingCheque.es_cpd}
                  onChange={(e) => setEditingCheque({ ...editingCheque, es_cpd: e.target.checked })}
                  className="w-4 h-4 text-[#FF6B2B] border-gray-300 rounded focus:ring-[#FF6B2B]"
                />
                <label htmlFor="edit-cpd" className="text-sm text-gray-700">CPD</label>
              </div>
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="edit-discrepancia"
                  checked={editingCheque.discrepancia_monto}
                  onChange={(e) => setEditingCheque({ ...editingCheque, discrepancia_monto: e.target.checked })}
                  className="w-4 h-4 text-[#FF6B2B] border-gray-300 rounded focus:ring-[#FF6B2B]"
                />
                <label htmlFor="edit-discrepancia" className="text-sm text-gray-700">Discrepancia monto</label>
              </div>
            </div>
            <Input label="Monto en letras" value={editingCheque.monto_letras ?? ''} onChange={(e) => setEditingCheque({ ...editingCheque, monto_letras: e.target.value || null })} />
            <Textarea label="Observaciones" value={editingCheque.observaciones ?? ''} onChange={(e) => setEditingCheque({ ...editingCheque, observaciones: e.target.value || null })} />
            <div className="flex gap-3 pt-4">
              <Button variant="primary" onClick={handleSaveEdit} className="flex-1" disabled={saving}>
                {saving ? 'Guardando...' : 'Guardar cambios'}
              </Button>
              <Button variant="secondary" onClick={() => setEditingCheque(null)} className="flex-1">
                Cancelar
              </Button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
}
