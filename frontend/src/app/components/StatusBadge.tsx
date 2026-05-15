import { cn } from "../lib/utils";

type StatusType =
  | 'disponible' | 'reservado' | 'vendido'
  | 'pendiente' | 'cobrado' | 'depositado' | 'rechazado'
  | 'contado' | 'financiado' | 'permuta' | 'mixto'
  | 'saldo' | 'sena' | 'cuota' | 'otro';

const statusStyles: Record<StatusType, string> = {
  disponible: 'bg-green-50 text-green-700 border-green-200',
  reservado: 'bg-amber-50 text-amber-700 border-amber-200',
  vendido: 'bg-gray-100 text-gray-700 border-gray-200',
  pendiente: 'bg-amber-50 text-amber-700 border-amber-200',
  cobrado: 'bg-green-50 text-green-700 border-green-200',
  depositado: 'bg-blue-50 text-blue-700 border-blue-200',
  rechazado: 'bg-red-50 text-red-700 border-red-200',
  contado: 'bg-green-50 text-green-700 border-green-200',
  financiado: 'bg-blue-50 text-blue-700 border-blue-200',
  permuta: 'bg-amber-50 text-amber-700 border-amber-200',
  mixto: 'bg-pink-50 text-pink-700 border-pink-200',
  saldo: 'bg-green-50 text-green-700 border-green-200',
  sena: 'bg-blue-50 text-blue-700 border-blue-200',
  cuota: 'bg-amber-50 text-amber-700 border-amber-200',
  otro: 'bg-gray-100 text-gray-700 border-gray-200',
};

interface StatusBadgeProps {
  status: StatusType;
  className?: string;
}

export default function StatusBadge({ status, className }: StatusBadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium uppercase border',
        statusStyles[status],
        className
      )}
    >
      {status}
    </span>
  );
}
