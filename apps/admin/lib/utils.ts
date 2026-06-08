export function cn(...classes: (string | false | null | undefined)[]) {
  return classes.filter(Boolean).join(" ");
}

export function formatCurrency(value: number) {
  return new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
  }).format(value);
}

export function formatDate(value: string) {
  return new Intl.DateTimeFormat("pt-BR", {
    dateStyle: "short",
    timeStyle: "short",
  }).format(new Date(value));
}

export function formatPhone(phone: string) {
  if (phone.startsWith("+55") && phone.length >= 13) {
    const ddd = phone.slice(3, 5);
    const rest = phone.slice(5);
    return `+55 (${ddd}) ${rest.slice(0, 5)}-${rest.slice(5)}`;
  }
  return phone;
}
