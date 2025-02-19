import looker_sdk

class Looker:
    def __init__(self):
        self.sdk = looker_sdk.init40()

    def get_dashboard_queries(self, dashboard_id: str) -> dict:
        """
        Retrieves queries of a dashboard

        Args:
            dashboard_id (Str): Dashboard ID to use

        Returns:
            List[dict]: List of queries for each tile in the dashboard
        """
        dashboard_data = self.sdk.dashboard(dashboard_id=dashboard_id)
        filters = {}
        for filter in dashboard_data["dashboard_filters"]:
            dimension = filter["dimension"]
            value = filter["default_value"]
            filters[dimension] = value

        queries = []
        for element in dashboard_data["dashboard_elements"]:
            if query := element.get("query"):
                element_dict = {
                    "id": query["id"],
                    "view": query.get("view"),
                    "fields": query.get("fields"),
                    "model": query.get("model"),
                    "dynamic_fields": query.get("dynamic_fields", None),
                    "filters": filters,
                }
                query = self.sdk.create_query(element_dict)
                queries.append(query)
            else:
                continue
        return queries

    def run_inline_query(self, query: dict):
        """
        Runs Inline Queries in Looker

        Args:
            query (dict): Looker query to run inline

        Returns:
            Dict: Results of running Looker Query
            
        """
        return self.sdk.run_inline_query(body=query, result_format="csv")
