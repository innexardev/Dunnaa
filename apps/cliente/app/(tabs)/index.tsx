import type { Establishment } from "@dunnaa/shared";
import { useRouter } from "expo-router";
import { useCallback, useEffect, useState } from "react";
import {
  ActivityIndicator,
  FlatList,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";

import { ApiError, api } from "@/lib/api";

export default function HomeScreen() {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [items, setItems] = useState<Establishment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = useCallback(async (q?: string) => {
    setLoading(true);
    setError("");
    try {
      const res = await api.establishments.search({ q: q || undefined });
      setItems(res.items);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Erro ao buscar");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Encontre sua barbearia</Text>
      <TextInput
        style={styles.search}
        placeholder="Buscar por nome..."
        value={query}
        onChangeText={setQuery}
        onSubmitEditing={() => load(query)}
        returnKeyType="search"
      />

      {error ? <Text style={styles.error}>{error}</Text> : null}
      {loading ? (
        <ActivityIndicator style={{ marginTop: 24 }} color="#16a34a" />
      ) : (
        <FlatList
          data={items}
          keyExtractor={(item) => item.id}
          contentContainerStyle={{ paddingBottom: 24 }}
          ListEmptyComponent={<Text style={styles.empty}>Nenhum estabelecimento encontrado</Text>}
          renderItem={({ item }) => (
            <Pressable
              style={styles.card}
              onPress={() => router.push(`/establishment/${item.id}`)}
            >
              <Text style={styles.name}>{item.name}</Text>
              <Text style={styles.meta}>
                {item.city}, {item.state}
              </Text>
              {item.distance != null && (
                <Text style={styles.meta}>{item.distance.toFixed(1)} km</Text>
              )}
            </Pressable>
          )}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16, backgroundColor: "#fafafa" },
  title: { fontSize: 22, fontWeight: "700", marginBottom: 12 },
  search: {
    borderWidth: 1,
    borderColor: "#ddd",
    borderRadius: 8,
    padding: 12,
    backgroundColor: "#fff",
    marginBottom: 12,
  },
  card: {
    backgroundColor: "#fff",
    borderRadius: 12,
    padding: 16,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: "#eee",
  },
  name: { fontSize: 16, fontWeight: "600" },
  meta: { fontSize: 13, color: "#666", marginTop: 4 },
  error: { color: "#dc2626", marginBottom: 8 },
  empty: { textAlign: "center", color: "#888", marginTop: 32 },
});
