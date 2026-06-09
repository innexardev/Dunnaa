import type { QueueEntry } from "@dunnaa/shared";
import { useEffect, useState } from "react";
import { ActivityIndicator, FlatList, StyleSheet, Text, View } from "react-native";

import { ApiError, api } from "@/lib/api";

export default function QueueScreen() {
  const [items, setItems] = useState<QueueEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    (async () => {
      try {
        setItems(await api.queue.my());
      } catch (e) {
        setError(e instanceof ApiError ? e.message : "Erro ao carregar fila");
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator color="#16a34a" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {error ? <Text style={styles.error}>{error}</Text> : null}
      <FlatList
        data={items}
        keyExtractor={(item) => item.id}
        ListEmptyComponent={<Text style={styles.empty}>Você não está em nenhuma fila</Text>}
        renderItem={({ item }) => (
          <View style={styles.card}>
            <Text style={styles.position}>Posição {item.position}</Text>
            <Text style={styles.status}>{item.status}</Text>
          </View>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16, backgroundColor: "#fafafa" },
  center: { flex: 1, justifyContent: "center", alignItems: "center" },
  card: {
    backgroundColor: "#fff",
    borderRadius: 12,
    padding: 16,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: "#eee",
  },
  position: { fontSize: 18, fontWeight: "700", color: "#16a34a" },
  status: { fontSize: 13, color: "#666", marginTop: 4, textTransform: "capitalize" },
  error: { color: "#dc2626", marginBottom: 8 },
  empty: { textAlign: "center", color: "#888", marginTop: 32 },
});
